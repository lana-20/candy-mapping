# PNSQC 2026 — Poster Paper Proposal (candy-mapping)

**Submission needs:** title · abstract 250–500 words · short bio · optional sketch
**Deadline:** rolling, closes when spots fill or **Sept 22, 2026**
**Notification:** Sept 24 · first draft poster to reviewer Sept 28 · feedback Sept 30
**Conference:** **Oct 12–14, 2026**
**Perk:** 50% off registration for accepted poster authors
**Contact:** program committee, pnsqc.org/conference/2026/poster/

This is the **sole PNSQC 2026 submission** — the sibling Vibium AX poster
(`~/pnsqc-2026-poster`) was archived 2026-08-04 in favor of this one, so the question of
whether PNSQC allows multiple submissions from one author no longer applies.

---

## Framing

**The AUT.** CandyMapper.com — Paul Grossman's "Website That Goes Wrong," a sandbox built
specifically to be broken: a contact-form journey wrapped around eleven planted defects
and eight hidden references. Grossman also publishes a public speed grid comparing
commercial testing tools' build-time vs run-time on the same challenge, which gives this
poster an existing community context to plug into.

**The finding.** One of the form's defects is invisible to slow testing by construction,
not by accident. The Submit button is clickable before its own handler finishes wiring
up. The first click after page load registers on a capture-phase listener and is silently
discarded — no error, no request, nothing to notice. Click again and it works. This
reproduces with a bare `element.click()` in the console, ruling out an automation
artefact — it is a real hydration race in the page.

**The method.** Three techniques, each reusable on any suspected startup race:
`attribute.sh` proves site-fault vs tool-fault by pairing a capture-phase click counter
with a network listener; `probe.sh` takes one timed attempt; `bisect.sh` sweeps delay and
narrows to the failure boundary. On the reference target the boundary is sharp — originally
3.7s discards, 4.2s succeeds — but not fixed: it moved by roughly two seconds within a
single later session. Sharp and drifting are not contradictory; the finding is deterministic
at any given moment, and the moment moves.

**The comparison.** Originally 60 runs (30/30 CLI, 0/30 MCP), hardened 2026-08-04 to 100
independent runs (50 CLI + 50 MCP) of the full eight-step canonical journey. The scripted
runner's median arrival rose to ~4.7s (from the original ~1s) — still inside the window:
49/50 hit the bug. The MCP agent's median stayed ~21.3s — still outside: 50/50 avoided it.
The finding held under harder replication; the margin did not — the 25× arrival gap first
measured is really ~4.6× once the boundary itself is accounted for (see below). A human
moving a mouse falls in the same slow category and structurally cannot see this defect
either.

**The boundary is not fixed.** Re-bisected properly (multiple probes, not one click) twice
more in the same 2026-08-04 session: 3,941→4,252ms after ~45 minutes, 4,095→4,393ms after
~90 minutes — a consistent ~150–250ms creep each time. The window drifts within a single
session, not just session to session, modestly and repeatably — a finding as worth
presenting as the original race itself.

**Positioning rules for the poster and the easel demo.** Vibium is presented purely as an
open-source project. No call to action, no download prompt, no commercial framing, no
comparison-shopping against other tools. The demo should be warm and easy to walk up to —
the two-minute repro: cold cache, fill two required fields, click Submit under four
seconds, watch the network, let people ask questions. The findings are reported warts and
all, including the corrected drift claim (the first version overstated it, on a single
click, before a proper re-bisection) and the CLI's own negative-path miss (0/50); that
honesty is the invitation. Anyone curious can re-run the whole thing from the published
scripts, which is the only "next step" the poster offers.

---

## Title

**The Window Is Four Seconds Wide — and It Moves: A Bug Scripted Testing Caught 49/50 and Deliberate Testing Never Saw**

Alternates:
- Too Slow to See It: A Four-Second Blind Spot in Autonomous Testing
- Quality in the Age of Autonomy: When Deliberation Costs You the Bug
- The Click That Never Lands: Measuring a Startup Race Invisible to Careful Testers
- The Boundary Moved and the Finding Didn't: Hardening a Startup Race to n=100

Ties to the 2026 theme **"Quality in the Age of Autonomy"**: most of the conversation
around autonomous testers asks whether their *judgment* is reliable; this poster asks
whether their *pace* determines what they can perceive at all — deliberation, usually
framed as safer testing, here erases an entire defect class.

---

## Abstract (draft, ~480 words)

CandyMapper.com is a sandbox built by tester Paul Grossman specifically to be broken: a
contact form wrapped around eleven planted defects and eight hidden references, daring
testers to find them by hand or by tool. One of those defects turned out to be invisible
to slower testers by construction, not by accident.

The contact form's Submit button is clickable before its handler finishes wiring up. The
first click after page load lands, registers on a capture-phase listener, and is silently
discarded — no error, no network request, nothing a user or a validator would notice.
Click again and it works. A plain `element.click()` typed into the console reproduces it,
ruling out an automation artefact.

I measured the window directly: repeated submissions at increasing delays after load
locate a sharp boundary, originally 3.7–4.2 seconds. Below it, every click is swallowed.
Above it, every click succeeds. It is a deterministic race with a millisecond-precise
edge — but the edge itself is not fixed. Re-bisecting properly (a full sweep, not a
single click) twice more in the same session found the window at 3.9–4.3 seconds after
about 45 minutes, then 4.1–4.4 seconds after about 90 — a consistent 150–250ms creep each
time. The boundary drifts within a single session, not only session to session, modestly
and repeatably.

I drove the same eight-step journey sixty times, split evenly between a scripted Vibium
CLI runner and an agent-driven Vibium MCP session — same site, same selectors, same
browser build. The scripted runner reached Submit about a second after filling the form,
always inside the window: it hit the bug 30 times out of 30. The MCP agent, deliberating
over each step, took roughly 25 seconds to arrive — always outside the window: it hit the
bug 0 times out of 30.

Then I hardened it: 100 independent runs (50 CLI, 50 MCP) of the full canonical journey,
a separate day. The scripted runner's median arrival rose to ~4.7 seconds — inside the
(moved) window 49 times out of 50. The agent's median arrival held near 21 seconds —
outside it, 50 times out of 50. The finding survived harder replication; its margin did
not. The 25× arrival gap first measured is closer to 4.6× once the boundary's own drift
is accounted for — a real result, and a caution against quoting a single ratio as if it
were a property of the tools rather than a snapshot of one measurement moment.

A second, quieter race turned up along the way: submitting with no email should show a
validation error before the real submit — the negative path a careful tester would check
first. The CLI's own attempt at that click is fast enough to be swallowed by the identical
race (confirmed 0 of 50 times); the agent's is not (confirmed 50 of 50). Even a scripted
test's own precondition check can be the thing the bug hides from.

That inverts an intuition "Quality in the Age of Autonomy" invites: more deliberation is
usually framed as safer testing. Here, deliberation cost the tester an entire class of
defect — while simultaneously being the only thing reliable enough to verify its own
negative-path assertion. Test speed is not a CI line item — it is the aperture that
decides which hydration and startup races a suite can even perceive, and which of a
suite's own checks it can trust.

I will bring the raw timing data from both measurement passes, the attribution technique
that proves the page — not the tooling — is at fault, and a live two-minute repro anyone
can run against their own site: cold cache, fill the two required fields, click Submit
under four seconds, watch the network. I will also show how the probe/attribute/bisect
method generalizes beyond this one bug to any suspected startup race.

---

## Bio (94 words — shared with the Vibium AX poster)

**Lana Begunova** is an AI, UI, and API SDET with seven years in test automation and the
founder of Daisy Lady Bug, a test automation consultancy in Seattle. She works in
Selenium, Playwright, Appium, and WebDriver BiDi, and spends most of her research time on
agent-driven browser automation. She is credited in the Vibium v26.5.31 release for "an
extraordinary amount of systematic, cross-client testing," having filed 40+ defects across
its CLI, MCP server, and JavaScript, Python, and Java clients. She publishes her
benchmarks and methodology openly at github.com/lana-20. ISTQB CTFL, AWS CCP, CSM.

---

## Poster artifacts — built and hardened

`assets/poster-board.html` (A0 print) and `assets/poster.html` (web companion) built from
`assets/poster_data.json`, which now carries both the original 2026-07-27 measurement and
the 2026-08-04 hardening (`hardening` key) side by side — the board and companion present
both, with the hardened n=50/50 numbers as the headline and the original as provenance.
Screenshot-verified in-browser 2026-08-04.

## Before submitting — open items

- [x] Moot — the sibling Vibium AX poster was archived 2026-08-04; this is now the only
      PNSQC 2026 submission from this author.
- [x] Verified attribution wording for CandyMapper / Paul Grossman — every mention credits
      him for the sandbox and separately for the published speed grid, in factual past
      tense ("built," "published," "his work"), with no phrase implying endorsement,
      collaboration, or review of this project's findings.
- [x] Moot — the sibling poster is archived, not being presented, so there's nothing to
      reference at the easel.
- [x] Re-verify the 3.7–4.2s window and the 30/30 vs 0/30 split — done 2026-08-04, at
      n=50/50 with the full canonical journey: 49/50 CLI, 50/50 MCP, boundary confirmed
      to drift within a session (not a fixed 3.7–4.2s). See `references/timing-methodology.md`
      and `references/test-case.md` in the main `candy-mapping` repo for full method.
- [x] Moot — bio originated from the sibling poster, but that poster is archived and not
      being submitted, so there's nothing left to keep in sync.
- [x] Decided not to disclose or track the hardening's real run cost anywhere published —
      it's an artifact of this account's usage, not a property of the finding.
