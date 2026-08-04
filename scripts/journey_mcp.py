#!/usr/bin/env python3
"""
Agent-driven arm of the CLI-vs-MCP hit-rate comparison. Same 8-step journey as
journey_cli.sh, driven by a Claude agent through the vibium MCP server instead of a
script. Modeled directly on the sibling PNSQC harness's run_task.sh / collect.py /
metrics.py — same isolation approach (fresh browser per run, no Bash access so the
agent cannot shell out to the vibium binary), same navigate/tool_use timestamp-pairing
technique for deriving elapsed time from the stream-json transcript.

  python3 journey_mcp.py [n_runs]        default 10

Resumable: skips any run_NN.json that already exists.

Grading is NOT the agent's own structured answer — it is a direct read of the LAST
tool_result in the transcript whose text is exactly "worked" or "SWALLOWED", produced
by instructing the agent to make its final tool call the identical detector-read JS
that journey_cli.sh and probe.sh already use. Ground truth from the page, not from what
the agent believes happened.
"""

import json
import re
import subprocess
import sys
import time
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "runs" / "mcp"
MODEL = "claude-sonnet-5"
BUDGET_USD = "0.50"
TIMEOUT_S = 300  # generous — MCP arm's own arrival time alone runs ~25s, plus reasoning

VIBIUM = "/usr/local/bin/vibium"

# Same success pattern and detector snippets as scripts/config.sh / probe.sh / journey_cli.sh.
SUCCESS = "thank you for your inquiry"
ARM_JS = (
    'window.__hit="";window.__before=document.body.innerText;'
    "new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes){"
    f'const s=(n.innerText||n.textContent||"");if(new RegExp("{SUCCESS}","i").test(s)&&s.length<400)'
    'window.__hit=s.trim()}}).observe(document.body,{childList:true,subtree:true});"armed"'
)
READ_JS = (
    "(()=>{"
    f'const re=new RegExp("{SUCCESS}","i");'
    "const appeared = re.test(document.body.innerText) && !re.test(window.__before||\"\");"
    'return (window.__hit || appeared) ? "worked" : "SWALLOWED"'
    "})()"
)
VALIDATION_TEXT = "Please enter a valid email address"
VALIDATION_JS = f'document.body.innerText.includes("{VALIDATION_TEXT}")'

PROMPT = f"""Drive candymapper.com's contact form through the vibium MCP browser tools.
Follow these steps exactly, in order:

1. browser_navigate to https://candymapper.com/
2. Dismiss the Pop-Up Challenge modal (click the element matching selector
   "[id$=-close-icon]", waiting for it to be visible first).
3. Scroll down to Contact Us — scroll input[data-aid="First Name"] into view (the
   section heading itself has no stable selector, see references/selectors.md).
4. Fill input[data-aid="First Name"] with "Test"
5. Fill input[data-aid="Last Name"] with "Testerson"
6. Click button[data-aid="CONTACT_SUBMIT_BUTTON_REND"] (no email filled yet — this is
   expected to trigger a validation error; it is not the click being measured, do not
   stop or report failure because of it)
7. Call browser_evaluate with EXACTLY this expression (character for character) to
   confirm the validation error actually appeared. This is an assertion, not optional —
   report what it returns, but continue to the next step regardless of the result:
   {VALIDATION_JS}
8. Fill input[data-aid="CONTACT_FORM_EMAIL"] with "test@example.invalid"
9. Call browser_evaluate with EXACTLY this expression (character for character, do not
   modify it) to arm a detector before the real submit:
   {ARM_JS}
10. Click button[data-aid="CONTACT_SUBMIT_BUTTON_REND"] again — this is the click that
    actually matters.
11. Wait about 3 seconds.
12. Call browser_evaluate with EXACTLY this expression (character for character) as your
    LAST tool call, and make no further tool calls after it:
    {READ_JS}

Do not use any tool other than the browser_* MCP tools. Do not fetch the page any other
way. Do not open any URL other than https://candymapper.com/. After step 12, just report
what the evaluate call returned in one short sentence — no other analysis needed.
"""


def ts(e):
    t = e.get("timestamp")
    if not t:
        return None
    return datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()


def load_events(path):
    events = []
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def tool_uses(events):
    """(id, name, input, timestamp) for every tool_use block, in order."""
    out = []
    for e in events:
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                out.append((b.get("id"), b.get("name", ""), b.get("input") or {}, ts(e)))
    return out


def result_text(c):
    """tool_result.content is a list of blocks ({"type":"text","text":...}), not a bare
    string — join the text blocks. Confirmed live 2026-08-04: json.dumps-ing the whole
    list instead of extracting this was the first bug that broke result detection on the
    dry run (a literal "worked" response was never matched because the actual value
    being compared was '[{"type": "text", "text": "worked"}]')."""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""


def tool_results(events):
    """tool_use_id -> (result text, timestamp)."""
    out = {}
    for e in events:
        if e.get("type") != "user":
            continue
        content = (e.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                out[b.get("tool_use_id")] = (result_text(b.get("content")), ts(e))
    return out


def derive(events):
    uses = tool_uses(events)
    results = tool_results(events)

    # Tool names carry the server prefix — confirmed live 2026-08-04:
    # "mcp__vibium__browser_navigate", not bare "browser_navigate". Match by suffix so
    # this survives the MCP server being registered under a different local name.
    def is_tool(name, base):
        return name == base or name.endswith("__" + base)

    nav_ts = next((t for _, n, i, t in uses if is_tool(n, "browser_navigate") and t), None)

    # Last click on the submit button, by name OR by an evaluate call containing the
    # selector (in case the agent used evaluate instead of browser_click for step 8).
    submit_ts = None
    for _, name, inp, t in reversed(uses):
        if not t:
            continue
        blob = json.dumps(inp)
        if "CONTACT_SUBMIT_BUTTON_REND" in blob and (is_tool(name, "browser_click") or is_tool(name, "browser_evaluate")):
            submit_ts = t
            break

    arrival_ms = None
    if nav_ts and submit_ts and submit_ts >= nav_ts:
        arrival_ms = round((submit_ts - nav_ts) * 1000)

    # Ground truth: the LAST tool_result whose text is exactly "worked" or "SWALLOWED"
    # — the deterministic return value of READ_JS, not the agent's opinion. Logged as
    # the literal string (matching journey_cli.sh), never a "hit" boolean — that field
    # name inverted its own meaning once already this session (hit=true turned out to
    # mean "worked", not "hit the bug") and cost a re-check before it reached real data.
    result = None
    for tid, name, inp, t in reversed(uses):
        if not is_tool(name, "browser_evaluate"):
            continue
        res = results.get(tid)
        if not res:
            continue
        text = res[0].strip().strip('"')
        if text in ("worked", "SWALLOWED"):
            result = text
            break

    # Same idea as journey_cli.sh's assertion: find the evaluate call that checked for
    # the validation-error text, read what it actually returned — not just that the
    # agent said it clicked submit #1.
    validation_confirmed = None
    for tid, name, inp, t in uses:
        if not is_tool(name, "browser_evaluate"):
            continue
        if "valid email address" not in json.dumps(inp):
            continue
        res = results.get(tid)
        if res:
            validation_confirmed = res[0].strip().strip('"') == "true"
        break

    return arrival_ms, result, validation_confirmed


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    OUT.mkdir(parents=True, exist_ok=True)

    claude_bin = subprocess.run(["command", "-v", "claude"], shell=False,
                                 capture_output=True, text=True)
    # `command -v` needs a shell; do it properly.
    claude_bin = subprocess.run("command -v claude", shell=True, capture_output=True, text=True).stdout.strip()
    if not claude_bin:
        print("claude not found on PATH", file=sys.stderr)
        sys.exit(2)

    for i in range(1, n + 1):
        run = f"{i:02d}"
        result_file = OUT / f"run_{run}.json"
        if result_file.exists():
            print(f"[mcp {run}/{n}] already exists, skipping")
            continue

        print(f"[mcp {run}/{n}] starting")
        work = OUT / f"_work_{run}"
        work.mkdir(exist_ok=True)
        mcp_config = work / "mcp.json"
        mcp_config.write_text(json.dumps({
            "mcpServers": {
                "vibium": {
                    "command": VIBIUM, "args": ["mcp"],
                    "env": {"PATH": "/usr/local/bin:/usr/bin:/bin"},
                }
            }
        }))

        subprocess.run([VIBIUM, "stop"], capture_output=True)  # fresh browser per run

        jsonl_path = work / f"run_{run}.jsonl"
        ts_start = datetime.datetime.now(datetime.timezone.utc).isoformat()
        t0 = time.time()

        with open(jsonl_path, "wb") as out_f:
            proc = subprocess.run(
                [
                    claude_bin, "-p", PROMPT,
                    "--model", MODEL,
                    "--output-format", "stream-json", "--verbose",
                    "--strict-mcp-config",
                    "--no-session-persistence",
                    "--max-budget-usd", BUDGET_USD,
                    "--mcp-config", str(mcp_config),
                    "--allowedTools", "mcp__vibium",
                    "--disallowedTools", "Bash", "WebFetch", "WebSearch", "Task",
                ],
                stdout=out_f, stderr=subprocess.PIPE, timeout=TIMEOUT_S,
                cwd=str(work),
            )
        wall_ms = round((time.time() - t0) * 1000)

        # Confirmed live 2026-08-04: `claude -p` reports rate-limit/credit exhaustion as a
        # structured event in STDOUT (the jsonl stream), not stderr — checking stderr
        # alone let 28 doomed calls run to instant, zero-cost failure before this was
        # first caught. But a naive text search for "rate_limit"/"out_of_credits" is a
        # false positive on EVERY run: every jsonl includes a routine
        # {"type":"rate_limit_event","rate_limit_info":{"status":"allowed",
        # "overageStatus":"rejected","overageDisabledReason":"out_of_credits",...}} even
        # on full success — overageStatus is a static account property (this account has
        # no overage), not a per-run failure signal. The real rejection sets the EVENT's
        # own top-level "status" to "rejected", and the run's terminal result carries
        # "is_error":true with "error":"rate_limit" / "api_error_status":429. Match on
        # those specifically, not on substrings that appear in healthy runs too.
        stderr_text = proc.stderr.decode(errors="replace")
        stdout_text = jsonl_path.read_text(errors="replace")
        fatal_pattern = re.compile(
            r'"rate_limit_info":\s*\{\s*"status":\s*"rejected"|'
            r'"error":\s*"rate_limit"|"api_error_status":\s*429|'
            r"you've hit your session limit|"
            r"invalid[_ ]api[_ ]key|authentication_error|credit balance", re.I)
        if fatal_pattern.search(stderr_text) or fatal_pattern.search(stdout_text):
            print(f"  FATAL (credits/auth) — aborting batch; re-run to resume\n{stderr_text[:500]}")
            sys.exit(4)

        events = load_events(jsonl_path)
        arrival_ms, result, validation_confirmed = derive(events)

        result_event = next((e for e in events if e.get("type") == "result"), {})
        cost_usd = result_event.get("total_cost_usd")

        record = {
            "run": i, "ts_start": ts_start, "model": MODEL,
            "arrival_ms": arrival_ms, "wall_ms": wall_ms,
            "cost_usd": cost_usd, "rc": proc.returncode,
            "validation_confirmed": validation_confirmed,
            "result": result if result is not None else "undetermined",
        }
        result_file.write_text(json.dumps(record, indent=2))
        print(f"[mcp {run}/{n}] arrival={arrival_ms}ms result={record['result']} "
              f"wall={wall_ms}ms cost=${cost_usd} rc={proc.returncode}")

        # Keep the raw transcript for audit, drop the throwaway mcp.json.
        (OUT / f"run_{run}.jsonl").write_bytes(jsonl_path.read_bytes())
        import shutil
        shutil.rmtree(work, ignore_errors=True)

        subprocess.run([VIBIUM, "stop"], capture_output=True)
        time.sleep(2)  # pace real submissions to the live site

    subprocess.run([VIBIUM, "daemon", "stop"], capture_output=True)
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
