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

**The tool.** Vibium (OSS browser automation) exposes two surfaces built to be driven by
a model: a **CLI** for deterministic, scripted automation, and an **MCP server** that
gives a coding agent the same browser control as a first-class tool call — Vibium as the
verification layer for coding agents, the way a debugger or a linter is a verification
layer for a human. This poster compares the two surfaces' natural pace against the same
browser action, not their tool logic: the CLI issues a raw `.click()`, the MCP arm reasons
about each step and calls the identical underlying action. Same daemon, same
Chrome-for-Testing build, same click — the only variable is how the caller gets there.

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
3.7s discards, 4.2s succeeds — but not fixed: it crept forward by 150–250ms per
re-measurement within a single later session (see below). Sharp and drifting are not
contradictory; the finding is deterministic at any given moment, and the moment moves.

**The comparison.** Originally 60 runs (30/30 CLI, 0/30 MCP), hardened 2026-08-04 to 140
independent runs (70 CLI + 70 MCP) of the full eight-step canonical journey. The scripted
runner's median arrival rose to ~4.7s (from the original ~1s) — still inside the window:
69/70 hit the bug. The MCP agent's median stayed ~22.0s — still outside: 70/70 avoided it.
The finding held under harder replication; the margin did not — the 25× arrival gap first
measured is really ~4.7× once the boundary itself is accounted for (see below). A human
moving a mouse falls in the same slow category and structurally cannot see this defect
either.

**Why MCP is slower, mechanically** (poster/methods framing, not for the abstract's word
budget): not the browser layer — both arms pay the same ~170–250ms per actual browser
action underneath. The CLI script issues all 8 steps back to back with no thinking between
them. The MCP agent re-reasons at every one of those 8 steps — reads the previous tool
result, decides the next tool call, then calls it — so the gap is 8 stacked reasoning
turns, not one slow step. See `references/timing-methodology.md` and
`vibium-mcp-flow.html` (traces one such turn stage by stage) in the main repo.

**Robustness check: does optimizing MCP close the gap?** (poster/methods framing, not
for the abstract's word budget). A separate, sibling investigation
(`~/vibium-efficiency`) asked whether the arrival gap is a property of MCP itself or
just of an un-optimized agent, and hardened a real answer: batching the journey's
independent tool calls into fewer reasoning turns (n=50 runs, not a demonstration) cuts
MCP's median arrival from ~22.0s to ~17.3s — a genuine ~25–27% speedup, with each
batched call still individually verified, not collapsed into an unverified shortcut.
It still misses the 3.7–4.4s window by roughly 4×. Speed isn't the fix; the finding
survives real optimization, not just the un-optimized baseline this poster otherwise
reports.

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
click, before a proper re-bisection) and the CLI's own negative-path miss (0/70); that
honesty is the invitation. Anyone curious can re-run the whole thing from the published
scripts, which is the only "next step" the poster offers.

---

## Title

**Quality in the Age of Autonomy: When Deliberation Costs You the Bug**

Alternates:
- The Window Is Four Seconds Wide — and It Moves: A Bug Scripted Testing Caught 69/70 and Deliberate Testing Never Saw
- Too Slow to See It: A Four-Second Blind Spot in Autonomous Testing
- The Click That Never Lands: Measuring a Startup Race Invisible to Careful Testers
- The Boundary Moved and the Finding Didn't: Hardening a Startup Race to n=140

Takes the 2026 theme title directly, on purpose: most of the conversation around
autonomous testers asks whether their *judgment* is reliable; this poster asks whether
their *pace* determines what they can perceive at all — deliberation, usually framed as
safer testing, here erases an entire defect class.

---

## Abstract (499 words)

CandyMapper.com is a sandbox built by tester Paul Grossman specifically to be broken: a
contact form wrapped around eleven planted defects and eight hidden references, daring
testers to find them by hand or by tool. One of those defects is invisible to slower
testers by construction, not by accident.

The contact form's Submit button is clickable before its handler finishes wiring up. The
first click after page load lands, registers on a capture-phase listener, and is silently
discarded — no error, no network request, nothing a user or a validator would notice.
Click again and it works. A plain `element.click()` typed into the console reproduces it,
ruling out an automation artefact.

I measured the window directly: repeated submissions at increasing delays locate a sharp
boundary, originally 3.7–4.2 seconds — below it every click is swallowed, above it every
click succeeds, a deterministic race with a millisecond-precise edge. But the edge moves:
re-bisecting properly (a full sweep, not one click) twice more in the same session found
it creeping forward 150–250ms each time, to 4.1–4.4 seconds 90 minutes later. It drifts
within a single session, not only session to session.

I drove the same eight-step journey through Vibium — the verification layer for coding
agents — on both its surfaces: a scripted CLI runner and an agent-driven MCP session, same
site, same selectors, same browser build. An original 60-run pass found CLI always inside
the window (30/30), MCP always outside it (0/30). Hardened to 140 independent runs of the
fuller journey on a separate day, the finding held while its margin narrowed: CLI's
median arrival rose to ~4.7s, still inside the moved window (69/70); MCP held near 22s,
outside it (70/70). The 25× arrival gap first measured is closer to 4.7× once the
boundary's own drift is accounted for.

Why MCP is slower isn't the browser layer, paid identically by both — it's 8 stacked
reasoning turns, one per step, against a script issuing all 8 back to back.

A second, quieter race turned up: submitting with no email should show a validation error
before the real submit, the negative path a careful tester checks first. The CLI's own
attempt at that click is fast enough to be swallowed by the identical race (0/70
confirmed); the agent's is not (70/70). Even a test's own precondition check can be what
the bug hides from.

That inverts an intuition "Quality in the Age of Autonomy" invites: deliberation is
usually framed as safer testing. Here it cost an entire class of defect while being the
only thing reliable enough to verify its own negative-path assertion. Test speed is the
aperture deciding which hydration races a suite can perceive, and which of its own checks
it can trust.

I will bring the raw timing data, the attribution technique proving the page — not the
tooling — is at fault, a live two-minute repro (cold cache, fill two fields, Submit under
four seconds, watch the network), and how probe/attribute/bisect generalizes to any
suspected startup race.

---

## Bio (99 words — no longer shared verbatim with the archived Vibium AX poster)

**Lana Begunova** is an AI, UI, and API SDET with seven years in test automation and the
founder of Daisy Lady Bug, a test automation consultancy in Seattle. She builds
automation frameworks with OSS tools like Selenium WebDriver BiDi, Appium, and now
Vibium, and spends most of her research time on agent-driven browser automation. She is
credited in the Vibium v26.5.31 release for "an extraordinary amount of systematic,
cross-client testing," having filed 40+ defects across its CLI, MCP server, and
JavaScript, Python, and Java clients. She publishes her benchmarks and methodology
openly at github.com/lana-20. ISTQB CTFL, AWS CCP, CSM.

---

## Poster artifacts — built and hardened

`assets/poster-board.html` (A0 print) and `assets/poster.html` (web companion) built from
`assets/poster_data.json`, which now carries both the original 2026-07-27 measurement and
the 2026-08-04 hardening (`hardening` key) side by side — the board and companion present
both, with the hardened n=70/70 numbers as the headline and the original as provenance.
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
      n=50/50 then hardened further to n=70/70 the same day, full canonical journey:
      69/70 CLI, 70/70 MCP, boundary confirmed to drift within a session (not a fixed
      3.7–4.2s). See `references/timing-methodology.md` and `references/test-case.md`
      in the main `candy-mapping` repo for full method.
- [x] Moot — bio originated from the sibling poster, but that poster is archived and not
      being submitted, so there's nothing left to keep in sync.
- [x] Decided not to disclose or track the hardening's real run cost anywhere published —
      it's an artifact of this account's usage, not a property of the finding.
- [ ] New 2026-08-05: added a "robustness check" paragraph citing `vibium-efficiency`'s
      hardened n=50 batched-MCP result (~17.3s median, still ~4× outside the window).
      Not yet reflected in the poster board/companion HTML or the abstract — decide
      whether this belongs in the printed poster itself (a footnote-sized addition) or
      stays proposal-only as talking-point backup for reviewer/easel questions.
