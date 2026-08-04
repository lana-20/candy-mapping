# Canonical test case — CandyMapper contact form

Recorded verbatim from the user, 2026-08-04. This is the exact sequence both
`journey_cli.sh` and `journey_mcp.py` implement — do not diverge from it without
updating this file first.

1. Go to https://candymapper.com/
2. Dismiss the pop-up by clicking 'x' or 'Find My Candy'
3. Scroll down to Contact Us
4. Fill in first and last name
5. Submit w/o mandatory email
6. Verify error 'Please enter a valid email address.'
7. Fill in email
8. Verify success message 'Thank you for your inquiry! We will get back to you within
   48 Years.'

Step 8 implies a second Submit click between step 7 and step 8 — not separately
numbered here, same as the article's own "eight-step" description, which has the
identical implicit-submit structure. The real submit (the one whose timing determines
hit/miss against the vulnerability window) is that second click.

## An important behavioral finding this surfaced (2026-08-04)

Step 5's submit click is **itself subject to the same startup race** as the real submit
in step 8. Verified directly: clicking submit with an empty email early (~2-3s after
load, the natural timing of a fast scripted run) is often silently swallowed — no
validation text appears at all, because the click handler that would show it never ran.
Clicking the identical submit late (tested at 5s after load, well past the boundary)
reliably shows "Please enter a valid email address."

Consequence: verifying step 6 with anything but a short, bounded timeout would force the
script to wait out the same window the real submit (step 8) is supposed to land inside —
which would make it structurally impossible for a fast run to ever hit the bug, since
confirming step 6 and racing step 8 pull in opposite directions. `journey_cli.sh` uses a
short bounded wait (800ms) for step 6's check: long enough to catch it when the click
does land after the window, short enough not to force every run past the window just to
verify a secondary step. A "false" reading on step 6 is informative (the click was raced),
not a script defect.

For `journey_mcp.py` the assertion is unconditional (the agent is instructed to check and
report, no timeout needed) — the agent's own reasoning time before reaching step 6 is
already comparable to or longer than the CLI's bounded wait, so this doesn't need the
same artificial cap. **Confirmed at n=70 each:** CLI reads `true` 0/70 times, MCP reads
`true` 70/70 times — exactly the predicted asymmetry, not a coincidence of a small sample.

## Audit log

**2026-08-04: both scripts confirmed step-for-step against this file.** `journey_cli.sh`
was missing the scroll step (step 3) for one earlier version; caught before it affected
the 50-run CLI batch (that batch already had it). `journey_mcp.py`'s prompt was missing
step 3 entirely in its first version — caught mid-batch, after 6 real paid runs had
already completed without it. Those 6 runs were archived (not counted) to
`data/runs/mcp_no_scroll_2026-08-04/`, the prompt fixed, and the batch restarted clean.
Both scripts now implement all 8 steps; `journey_mcp.py`'s prompt numbers 12 sub-steps
(splitting fill-first/fill-last and making arm/wait explicit for the agent) but every one
of the 8 canonical steps is represented. An initial 50/50 batch was extended to 70/70 the
same day, same harness (resumable, picked up at run 51 for each arm).

## Final results, 2026-08-04 (n=70 each, clean batches only)

| | CLI | MCP |
|---|---|---|
| result | 69 SWALLOWED / 1 precondition_failed / 0 worked | 70/70 worked |
| arrival time (median) | 4,710ms | 21,986ms |
| step 6 confirmed (`validation_confirmed`) | 0/70 | 70/70 |

Both arms' primary metric (does the real submit in step 8 hit the race) hardened the
original 30/30-vs-0/30 finding. Full numbers and the two harness bugs this batch
surfaced (rate-limit detection scanning the wrong stream, the missing scroll step) are in
`timing-methodology.md`'s "140-run hardening pass" section.
