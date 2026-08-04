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

**MCP side:** reasoning turns, not the browser or daemon, is the bottleneck — both
arms pay the same ~170–250ms per real action. Hand-rolling batched
`browser_evaluate` calls (collapsing several steps into one JS blob) measured a real
~1.4× speedup (n=20 real runs) but **produced a real correctness bug**: a "verify the
click happened" field that turned out to be a hardcoded `true` literal, not a real
check — caught and fixed mid-investigation, not before it was first trusted. Even
the *fixed*, verified version of batching only gets MCP arrival to ~15s — still
~3.5× outside the window. An off-the-shelf MCP proxy (callmux) that batches turns
while keeping each downstream tool call individually real and verified looks like a
more promising architecture than hand-rolled JS, but is completely untested against
Vibium specifically.

## The actual prospectus: what would be worth pitching, if this became real work

1. **The headline number, if this ever got built out properly:** "MCP agent overhead
   is dominated by turn count, not model intelligence or browser cost — and the
   cheapest way to cut it (collapsing steps into raw JS) is also the way most likely
   to quietly break verification. A safer path exists (proxy-level batching that
   keeps each tool call real) but is unproven." That's a genuinely interesting
   claim for an audience thinking about agent cost at scale, and it's grounded in
   the same verify-everything discipline this poster already demonstrates elsewhere
   (the drift-claim correction, the `bisect.sh` exit-code bug).
2. **Where it would NOT go:** never as a claim that batching changes the race-window
   finding. Every number in the underlying investigation confirms it doesn't, and
   restating that caveat is mandatory anywhere this surfaces, including here.
3. **What's missing before this is even pitch-ready:** the callmux avenue is
   completely unverified against Vibium; the hand-rolled-batching numbers are real
   but small-sample (n=20, not n≥50 the way the main finding was hardened); there is
   no cost/token accounting comparable to the arrival-time numbers (this
   investigation measured *time*, not *tokens* — a real gap for a "token
   optimization" pitch specifically, since token counts were never pulled from the
   transcripts).

## If this gets picked up

Start at `~/.claude/skills/vibium-efficiency/SKILL.md`. Do not copy its content back
into this file or into `PNSQC-PROPOSAL.md` — extend the skill, then decide separately
and deliberately whether a compressed version belongs in a submission, per the
account's standing "no public-facing files touched without being asked" rule that
governed the entire underlying investigation.

No next action yet.
