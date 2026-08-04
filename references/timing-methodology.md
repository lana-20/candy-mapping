# Timing methodology — how "t+Xms" is actually measured

This is the mechanism behind every millisecond figure this skill publishes (the 3.7–4.2s
window, the individual probe timestamps, the bisection). It is not covered by
`methodology.md`'s general findings — this is specifically about what the clock measures,
what it doesn't, and how precise the resulting numbers actually are.

## What clock is used, and why

`probe.sh` reads `performance.now()` from inside the page, not a shell-side timestamp:

```js
Math.round(performance.now())
```

`performance.now()` is monotonic, sub-millisecond resolution, and — critically — its zero
point is the page's own navigation start. That makes it the only correct clock for "how
long after page load was this click": a shell-side `date +%s%N` would measure time in a
different process, related to the page's timeline only via IPC round trips of unknown and
varying length.

## The bug this replaced

Until 2026-08-04, `probe.sh` captured the timestamp and fired the click as **two separate
CLI invocations**:

```bash
AGE=$($V eval 'Math.round(performance.now())')
$V click "$ACTION"
```

Each `vibium` CLI call is a separate process: spawn, connect to the daemon, round-trip to
the browser, return. Measured on this machine (2026-08-04, `vibium eval 'performance.now()'`
in a loop): **170–250ms per call.** That entire span sits, unaccounted for, between "the
instant we recorded" and "the instant the click actually reached the page" — because the
click command hadn't even been issued yet when the timestamp was taken.

This matters because the published boundary is only **512ms wide** (3,687ms discard →
4,199ms success). A single command's latency is the same order of magnitude as the whole
bracket. The qualitative finding (CLI arrives ~1s, MCP ~25s — three orders of magnitude
apart) was never at risk. The specific millisecond figures were claiming more precision
than a two-call mechanism could actually back up.

## The fix

Timestamp and click now happen inside **one** `eval` call, as a single synchronous JS
expression:

```bash
AGE=$($V eval "(()=>{const t=Math.round(performance.now());document.querySelector('${ACTION}').click();return t})()")
```

The page reads its own clock and dispatches the click in the same tick. There is no
inter-process gap left to account for — the number returned is, to sub-millisecond
precision, the real time-since-load at which the click fired.

**Trade-off, stated plainly:** this bypasses `vibium click`'s actionability checks
(visibility, scroll-into-view, obscured-element detection). A raw `.click()` fires
regardless of whether the element is actually clickable by a user. That's an acceptable
trade here because the button is already in view by this point in the flow (no scroll step
precedes it). It would **not** be acceptable to copy this pattern somewhere the target
might not be interactable yet — you'd trade timing precision for false SWALLOWED verdicts
on elements that were never really reachable.

## What is still not accounted for

- **`$V sleep "$DELAY_MS"` before the click** goes through the same CLI round-trip, but
  since it's a *wait*, not a *measurement*, its own latency doesn't bias the timestamp —
  it just means the requested delay and the actual elapsed time never match exactly. This
  is fine: `probe.sh` never treats `DELAY_MS` as the reported value, only `AGE` is. Read
  the printed `t+` figures, never the delay argument, when quoting a result.
- **Everything before the timed click** (navigate, dismiss modal, fill, read back, arm the
  observer) still goes through normal multi-call CLI overhead, which is why `AGE` values
  land well past their requested `DELAY_MS` (e.g. a `4000` request reporting `t+7093ms` is
  expected, not a bug — that gap is fixed setup cost, not race-window noise).
- **Network and server-side variance** on the live target are not controlled for. Numbers
  will drift run to run; `methodology.md` already documents this ("timing figures moved,
  one of them by 40%") and the standing rule to re-run before publishing still applies.

## Where the setup time actually goes

Measured directly (2026-08-04) by instrumenting every step of `probe.sh` with wall-clock
timestamps around each `vibium` CLI call, run once cold (nothing running beforehand) and
once warm (daemon and browser already up — the realistic case for every probe after the
first in one `bisect.sh` sweep, since it never stops the browser between probes).

| step | cold start (ms) | cold (%) | warm (ms) | warm (%) |
|---|---:|---:|---:|---:|
| `cookies clear` (`COLD_CACHE`) | 1,125 | 23.8% | 165 | 5.5% |
| `go` — navigate to URL | 1,491 | 31.6% | 613 | 20.3% |
| `wait` + `click` — dismiss modal | 652 | 13.8% | 769 | 25.5% |
| fill × 2 + read-back verify | 1,092 | 23.2% | 931 | 30.9% |
| `eval` — arm `MutationObserver` | 178 | 3.8% | 184 | 6.1% |
| `eval` — read `performance.now()` *(old two-call design)* | 179 | 3.8% | 170 | 5.6% |
| `eval` — combined timestamp + click *(current one-call design)* | — | — | 182 | 6.0% |
| **total setup before the timed click** | **4,717** | 100.0% | **3,014** | 100.0% |

Two things this makes concrete:

**Why `AGE` lands well past the requested `DELAY_MS`.** A `probe.sh 4000` call reports
`t+7093ms` not because anything is wrong — it's `4000` (requested sleep) plus roughly
`3000` of fixed setup that happens before the sleep even starts. The warm-run total above
(≈3,014ms) is that fixed cost. Never read `DELAY_MS` as the result; only the printed `t+`
figure is real.

**The fix's actual saving, not just its correctness.** The old design's two separate
calls — read `performance.now()` (170ms round trip) then a separate `click` (a
comparable ~180ms round trip) — cost roughly 350ms combined, with the entire gap between
them unaccounted for in the timestamp. The new single combined call costs 182ms **total**,
with zero gap between the timestamp being read and the click firing, because both happen
in the same synchronous JS tick server-side. The fix isn't just more honest about
precision, it's also roughly twice as fast for that step.

**Fill + dismiss-modal dominate warm-run setup** (56% combined), not the CLI's per-call
floor — consistent with `methodology.md`'s point that process-spawn overhead is real but
usually not the story. Cold start adds roughly 1.7s on top, almost entirely in daemon/
browser launch (`cookies clear` and `go` both pay a share of it, since either can be the
call that triggers the lazy launch).

**Scope: this table is the CLI arm only. No model/LLM calls are in it, or in any other
number on this page.** `probe.sh` is plain bash calling the `vibium` CLI directly —
`cookies clear`, `go`, `wait`, `click`, `fill`, `eval`. No `claude` invocation, no API
call, no agent loop anywhere in it. Every millisecond above is browser-automation
overhead: process spawn, daemon round-trip, page navigation, DOM interaction.

The MCP arm's "~25s to Submit" figure quoted elsewhere in this project (the article, the
poster) is a **different measurement, produced a different way**, and none of it is
decomposed here. That number came from **Claude Sonnet** driving through MCP tools in the
original 60-run benchmark (2026-07-27), deciding each step as it went — it includes model
inference latency, tool-call round trips, and reasoning time on top of whatever CLI/BiDi
overhead sits underneath. There is no step-by-step breakdown of it anywhere in this
project, unlike the CLI arm's table above. Do not treat the two figures as decomposing the
same kind of time, or try to net one against the other — they measure different machines
doing different things.

**Model/tooling record for the whole experiment** (both arms, confirmed with the author
2026-08-04 — not previously recorded anywhere in the repo, article, or `SKILL.md`):

| | |
|---|---|
| Scripted CLI arm | Vibium v26.5.31 CLI, no model — plain bash + `vibium` commands |
| Agent-driven MCP arm | Vibium v26.5.31 MCP server, driven by **Claude Sonnet** |
| Date | 2026-07-27, sixty runs across three sessions |
| Browser | Chrome for Testing, "each on its own Chrome build" per the article's endnote — exact build not separately pinned |

This table existed only as an unverified guess in the poster's disclosure footer
(`pnsqc-poster/assets/poster.html` / `poster-board.html`) before now — "Claude Sonnet" was
written there without a confirmed source. It has since been confirmed and now has a home;
treat this file, not the poster footer, as the source of record if the two ever disagree.

## The 100-run hardening pass, 2026-08-04

Independent of the original 60-run benchmark above — different date, fuller step
sequence (`references/test-case.md`'s canonical 8 steps, including the scroll step and
the negative-path assertion neither original arm explicitly checked), model pinned to
`claude-sonnet-5`. Full harness: `scripts/journey_cli.sh`, `scripts/journey_mcp.py`,
resumable, one JSON per run under `data/runs/{cli,mcp}/`.

| | CLI (n=50) | MCP (n=50) |
|---|---|---|
| result | 49 SWALLOWED / 1 precondition_failed / 0 worked | 50/50 worked |
| arrival time | min 4,430ms · max 5,042ms · median 4,684ms · mean 4,701ms (stdev 129ms) | min 17,480ms · max 28,881ms · median 21,330ms · mean 21,856ms (stdev 2,401ms) |
| negative path confirmed (`validation_confirmed`) | 0/50 | 50/50 |
| real cost | $0 (no model) | $11.71 |

**Arrival gap, recomputed:** 21,330 / 4,684 ≈ **4.6×** (medians) — down from the original
25× (25s / 1s). Not a contradiction: the original figure compared a first-pass ~1s CLI
arrival against ~25s MCP: two numbers from a leaner 2-field flow, an earlier session, and
(per the drift finding below) a since-moved boundary. The hardened figure compares the
full canonical journey, same session, same day. Both are real measurements of different
things; quote whichever one matches what's actually being compared.

**Two clean-batch discipline notes, both costly to learn:** (1) the account's 5-hour
session usage limit was hit mid-batch once; `claude -p` reports this as a structured
*stdout* event (`{"type":"rate_limit_event","rate_limit_info":{"status":"rejected",...}}`),
not stderr — `journey_mcp.py`'s original FATAL check only scanned stderr, so 28 calls ran
to instant, zero-cost failure before this was caught. Fixed to scan both, and to match on
the event's own `status` field rather than substrings that also appear on healthy runs
(`overageStatus`/`out_of_credits` are static account properties present in every run,
successful or not — an early, broader regex false-positived on run 1 of the very next
batch). (2) `journey_mcp.py`'s prompt omitted the canonical flow's scroll step in its
first version; caught after 6 real paid runs had already completed without it. Both
incidents' junk/incomplete runs were archived, not deleted or silently kept — see
`data/runs/mcp_no_scroll_2026-08-04/` and `data/runs/_rejected/rate_limit_2026-08-04/`.

## Precision this mechanism can actually defend

- Individual click timestamps: sub-millisecond, relative to page navigation start.
- The *existence* and *rough location* of a boundary: solid — this was never in doubt.
- A specific bracket width down to tens of milliseconds: only as good as the bisection's
  own stopping threshold (`bisect.sh` stops narrowing once the bracket is ≤400ms). Don't
  quote a bracket tighter than that threshold as if it were exact — the true transition
  could be anywhere inside the final bracket, not necessarily at its printed edges.

## Re-verification, 2026-08-04 (same-session, fixed-mechanism boundary)

Re-ran `bisect.sh` with the corrected single-eval mechanism, as part of planning the
100-run hardening batch — the published 3,687→4,199ms figure was measured with the old,
less precise two-call mechanism and had not been re-confirmed since the fix.

**Result: last discard at t+3,941ms, first success at t+4,252ms** — window ≈ **3.9–4.3s**.
Close to the original 3.7–4.2s, shifted a few hundred ms later. At the time, this looked
reassuring: the boundary hadn't moved dramatically, consistent with `methodology.md`'s
standing note that absolute timings drift session to session but behavioral findings
hold.

**That reassurance needed a real second measurement, not one click, to actually mean
anything — and the first attempt at "confirming" drift got exactly that wrong.**
~30–45 minutes later, building the 100-run journey harness, a plain single click with
zero prior interaction was fired at t+6,054ms and was still SWALLOWED. That single point
was written up here as proof the boundary had moved nearly two seconds — a single sample
being treated as if it were a re-bisection, the precise mistake this document's own
"Reporting standards" section (in `methodology.md`) warns against. It sat published,
uncorrected, across six files and two commits before being checked.

**Properly re-bisected (multiple probes, not one click), 2026-08-04, ~90 minutes into
the session: last discard at t+4,095ms, first success at t+4,393ms.** Three real
bisections across this one session now exist:

| When | Discard → success |
|---|---|
| Original, 2026-07-27 | 3,687ms → 4,199ms |
| Re-bisected, ~45 min into this session | 3,941ms → 4,252ms |
| Re-bisected, ~90 min into this session | 4,095ms → 4,393ms |

**The finding is real, and it is modest.** A consistent ~150–250ms creep per
re-measurement, same direction each time — genuine within-session drift, not the ~1.9s
jump the single control click implied. That click was very likely an outlier (network
jitter, a slow individual page load) rather than a representative sample of where the
boundary actually sat at that moment. `scripts/bisect.sh` also had a real bug found
during this re-measurement — its coarse sweep didn't distinguish a precondition failure
(fill didn't register) from a genuine SWALLOWED, so a corrupted probe could silently
enter the bracket; fixed to check the exit code explicitly instead of relying on bash
truthiness.

**Consequence for how to read every millisecond figure in this project:** treat any
bisected boundary as a snapshot valid for roughly the session in which it was measured,
not a stable constant to check new data against later — the drift is real, if modest.
Separately, and just as important: **one probe is a data point, not a bisection.** A
single click confirms nothing about a boundary on its own; only a real multi-probe
bisection does. If you need a boundary to compare against, re-bisect properly immediately
before, not 30 minutes before, and don't let a single control click stand in for one.
Quoting a bracket to the exact millisecond ("3,687ms discards, 4,199ms succeeds") remains
true of the moment it was measured — it is not a fact about the site that holds for the
rest of the day, and it should never rest on fewer than the several probes a real
bisection requires.

## Reproducing / verifying this

```bash
bash scripts/probe.sh 4000        # one timed click, single-eval mechanism
bash scripts/bisect.sh            # full sweep + bisection
```

Each live run is a real form submission against candymapper.com — keep probe counts low
per the skill's safety notice in `SKILL.md`. Don't hammer the endpoint while validating
harness changes; a handful of calls is enough to confirm the mechanism works, not to
re-establish the published window (that needs a fresh, isolated session, per
`methodology.md`'s "verify your own harness first" section).
