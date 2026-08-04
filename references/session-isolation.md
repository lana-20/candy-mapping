# Session isolation — does state leak between CLI and MCP?

Verified 2026-08-04 by directly probing the running daemon, not inferred from docs. This
matters for any benchmark that compares the CLI and MCP surfaces (this skill's own
30/30-vs-0/30 result, the sibling `vibium-agentic-challenge` work) — if the two surfaces
shared cookies, localStorage, or a browser profile, "run CLI and MCP against the same
target" would not be the clean A/B comparison it's presented as.

## The question

Both `vibium` (CLI) and `vibium mcp` (MCP server) talk to the same background
`vibium daemon` process. Does that shared daemon mean they also share browser state —
cookies, localStorage, the page itself — when run concurrently?

## The test

1. Start a CLI session, navigate to `https://example.com`, set a cookie:
   ```
   vibium start
   vibium go https://example.com
   vibium cookies "leaktest" "cli-value-12345"
   ```
2. **Without stopping the CLI session**, spawn a separate `vibium mcp` process (JSON-RPC
   over stdio), call `browser_start`, navigate it to the *same* origin, and read
   `document.cookie` from inside that MCP session.
3. Have the MCP session set its own cookie (`mcp-marker=xyz789`).
4. Switch back to the CLI session and read `document.cookie` again.

## The result

| Step | What happened |
|---|---|
| MCP `browser_start` while CLI session was open | `"Browser launched"` — **not** "already running." A fresh browser, not a reused one. |
| MCP's first page | `about:blank` — did not inherit the CLI's `example.com` navigation. |
| MCP navigates to `example.com`, reads `document.cookie` | `""` — empty. Did **not** see `leaktest=cli-value-12345`, despite identical origin. |
| MCP sets `mcp-marker=xyz789` | Succeeds, confirmed read-back within the MCP session. |
| CLI reads `document.cookie` again, after MCP set its cookie | `leaktest=cli-value-12345` only — **no** `mcp-marker`. |

Zero cross-contamination in either direction, on the identical origin, while both
sessions were live at once.

## Why: separate processes, not just separate logical contexts

`ps -eww` during the concurrent test showed two distinct Chrome-for-Testing processes,
each with its own `--user-data-dir`:

```
--user-data-dir=/var/folders/.../T/org.chromium.Chromium.scoped_dir.EgwgDt   (one session)
--user-data-dir=/var/folders/.../T/org.chromium.Chromium.scoped_dir.dtOzoQ   (another)
```

Each `vibium start` / MCP `browser_start` launches Chrome with a **fresh, randomly-named
temp profile directory**, created new per launch. Two different profile directories means
two entirely separate cookie jars, localStorage, and IndexedDB stores — real OS-level
isolation via separate processes and separate filesystem state, not merely two logical
contexts inside one shared browser.

## What actually is shared

Only the `vibium daemon` itself — one background OS process, one Unix socket
(`~/Library/Caches/vibium/vibium.sock`). Confirmed via `vibium daemon status`: same PID
served both the CLI calls and the MCP subprocess's requests throughout the test. But the
daemon behaves as a dispatcher that spins up a distinct Chrome subprocess per session,
not a router into one shared browser instance. No evidence of shared state living in the
daemon itself (no shared cookies, no shared page, no shared navigation state).

## The one place state genuinely does persist — and it's already handled

Not a CLI-vs-MCP problem: a **same-tool, multi-call** one. `vibium go` lazily
auto-starts a browser only if none is already running — confirmed by stopping both the
session and the daemon, then calling `vibium go` directly and watching it launch both
from cold. That means a script which calls the CLI repeatedly *without* an explicit
`stop` between calls reuses the same browser process and profile across all of those
calls.

This skill's own `bisect.sh` does exactly that — it calls `probe.sh` in a loop with no
`stop` in between, so every probe in one bisection run shares one browser process. That
is precisely why `config.sh` sets `COLD_CACHE=1`, which makes every `probe.sh` invocation
run `vibium cookies clear` before it does anything else. The guard is already correct and
already in place; this write-up is the reasoning behind why it's necessary, not a new
requirement.

## Bottom line

- **CLI vs MCP, run concurrently: isolated.** Separate processes, separate profiles,
  verified empirically on identical origins — safe to treat as a clean A/B comparison.
- **Same tool, sequential calls, no explicit restart: not isolated by default.** The
  browser process and its profile persist across calls until something calls `stop` (or
  the daemon is killed). Any script in this pattern needs its own version of `probe.sh`'s
  `COLD_CACHE` discipline — don't assume a fresh profile just because a new command ran.

## Reproducing this

```bash
vibium daemon stop
vibium start && vibium go https://example.com && vibium cookies "leaktest" "cli-value-12345"

python3 - <<'PY'
import subprocess, json
def send(p,o): p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
def recv(p): return json.loads(p.stdout.readline())
p = subprocess.Popen(["vibium","mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
send(p, {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}); recv(p)
send(p, {"jsonrpc":"2.0","method":"notifications/initialized"})
send(p, {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"browser_start","arguments":{}}}); print(recv(p))
send(p, {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"browser_navigate","arguments":{"url":"https://example.com"}}}); print(recv(p))
send(p, {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"browser_evaluate","arguments":{"expression":"document.cookie"}}}); print(recv(p))
p.stdin.close(); p.wait(timeout=5)
PY

vibium eval "document.cookie"   # back on the CLI side — should still only show leaktest
vibium stop; vibium daemon stop
```
