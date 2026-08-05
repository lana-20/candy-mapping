# Token/cost optimization — a prospectus, not a submission (poster side)

**Status: rumination, not part of `PNSQC-PROPOSAL.md`, not wired into any built
artifact.** This is a pitch for a possible future-work angle, kept separate from the
actual submission so it never accidentally leaks into the poster, companion, or
handout. The bulk investigation this summarizes lives entirely outside this repo, in
the standalone `vibium-efficiency` skill (`~/.claude/skills/vibium-efficiency/`) —
nothing here duplicates it in full; read that if you need the actual measurements,
transcripts, or scripts.

## Why this belongs near the poster, even unpublished

The poster's central claim is **"Quality in the Age of Autonomy: When Deliberation
Costs You the Bug"** — an MCP agent's own reasoning pace is what pushes it outside the
3.7–4.4s vulnerability window, so deliberation (normally framed as safer testing)
structurally blinds it to this defect class.

This prospectus asks the natural next question from the *opposite* angle: **if
deliberation is what costs an agent the bug, can deliberation itself be made cheaper —
in tokens, turns, and dollars — without losing the per-step verification that makes an
agent's judgment trustworthy in the first place?** That's not a rebuttal of the
poster's finding. It's the same tension (speed vs. safety) restated as a cost problem
instead of a timing problem, and it's the honest next question a reviewer or an
audience member is likely to ask at the easel: *"OK, MCP is slow and expensive here —
is that fixable, and does fixing it break anything?"*

## What was actually found (compressed — full detail in `vibium-efficiency`)

**CLI side:** process spawn, not the browser or daemon, is the bottleneck. ~87% of a
single `vibium eval` call's cost is OS process startup; the actual daemon+browser
round trip is only ~18ms. `vibium pipe` (one persistent process instead of one per
command) cuts marginal per-call cost by ~50–100× once warm, in a real measurement.
*Doesn't matter for the poster's finding* — the CLI arm already lands inside the
window on 69/70 hardened runs; making it faster only pushes it further inside a
window it already reaches.

**MCP side, per call: reasoning turns, not the browser or daemon, is the
bottleneck — now measured directly, not just inferred.** A later pass split
`tool_use`→`tool_result` (real browser/MCP round-trip time) from `tool_result`→next-
`tool_use` (model reasoning time) across this project's own n=70 real transcripts
(same dataset behind the poster's race-window finding). **Inside the exact
nav→timed-submit arrival window that decides whether an MCP agent's click lands
inside or outside the 3.7–4.4s race window: only 13.9% of that time (~3.1s median) is
real browser/MCP work — 86.1% (~19.1s median) is Claude thinking between calls.**
That's the same "~170–250ms per real action" claim as before, but as a measured
percentage of the window that actually matters, not an average per-call estimate.
Full method and data: `vibium-efficiency/references/model-vs-browser-wait-split.md`.

Hand-rolling batched `browser_evaluate` calls (collapsing several steps into one JS
blob) measured a real ~1.4× speedup (n=20 real runs) but **produced a real
correctness bug**: a "verify the click happened" field that turned out to be a
hardcoded `true` literal, not a real check — caught and fixed mid-investigation, not
before it was first trusted. Even the *fixed*, verified version of batching only gets
MCP arrival to ~15s — still ~3.5× outside the window. An off-the-shelf MCP proxy
(callmux) that batches turns while keeping each downstream tool call individually real
and verified looks like a more promising architecture than hand-rolled JS, but is
completely untested against Vibium specifically.

**MCP side, static (just having 85 tools connected):** turns out to be a
non-problem. Real measurement (confirmed twice): Vibium's full MCP tool surface
costs only ~1,353 tokens to have connected — 82% less than a naive raw-JSON estimate
(~7,549 tokens). This directly undercuts half of callmux's own pitch (schema
compression / "40+ tools bloating the system prompt") for Vibium specifically,
without touching its other half (batching per-call turns, still real and large).
**A genuinely interesting nuance for the pitch below:** the two "token optimization"
stories for MCP are not the same story, and the more dramatic-sounding one (schema
bloat) turned out to be the one that wasn't real here.

## The actual prospectus: what would be worth pitching, if this became real work

1. **The headline number, if this ever got built out properly:** "Inside the exact
   window that decides whether an MCP agent catches or misses this bug class, 86% of
   the time is Claude thinking — only 14% is Vibium or the browser doing anything.
   The cheapest way to cut that (collapsing steps into raw JS) is also the way most
   likely to quietly break verification. A safer path exists (proxy-level batching
   that keeps each tool call real) but is unproven." That's a genuinely interesting
   claim for an audience thinking about agent cost at scale, and it's grounded in
   the same verify-everything discipline this poster already demonstrates elsewhere
   (the drift-claim correction, the `bisect.sh` exit-code bug).
2. **Where it would NOT go:** never as a claim that batching changes the race-window
   finding. Every number in the underlying investigation confirms it doesn't, and
   restating that caveat is mandatory anywhere this surfaces, including here.
3. **What's missing before this is even pitch-ready:** the callmux avenue is
   completely unverified against Vibium; the hand-rolled-batching numbers are real
   but small-sample (n=20, not n≥50 the way the main finding was hardened); token
   accounting exists now for the *static* schema-connection cost (~1,353 tokens,
   real measurement) but still not for the *per-call* cost across a full batched
   journey — the arrival-time numbers (~1.4× speedup) have no token-count
   counterpart yet, which is the more relevant number for a "token optimization"
   pitch specifically.

## If this gets picked up

Start at `github.com/lana-20/vibium-efficiency` (private repo — the source of truth;
`~/.claude/skills/vibium-efficiency/` is a synced read copy, don't edit it directly).
Do not copy its content back into this file or into `PNSQC-PROPOSAL.md` — extend the
skill, then decide separately and deliberately whether a compressed version belongs
in a submission, per the account's standing "no public-facing files touched without
being asked" rule that governed the entire underlying investigation.

No next action yet.
