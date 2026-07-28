---
name: candy-mapping
description: Hunt startup and hydration race bugs in web UIs with the Vibium CLI — the class of defect where a click lands before the page is wired and is silently discarded. Measures the exact vulnerability window in milliseconds. Use when asked to candy-map a site, hunt race conditions, find timing bugs, investigate a button that "does nothing on the first click", check for hydration races, or test whether an action works at machine speed.
---

# Candy Mapping

Named for the CandyMapper sandbox where the method was worked out. The premise: a suite is an
instrument, and how fast it moves decides which defects it can perceive. Startup races are invisible
to manual testing and to slow agent-driven runs, and reproduce 100% of the time to anything quick.

Hunt them by racing the page, then measure the window in which it is vulnerable.

## Process Steps

1. **Confirm authorization.** Establish that the target is a sandbox, a staging environment, or a
   system the user owns. If it is production or a third party's site, stop and ask.
2. **Map the journey.** `vibium go <url> && vibium map`. Identify the action under test (usually a
   submit, save, or add-to-cart button) and the minimum steps to reach it.
3. **Establish stable locators before anything else.** Run `references/methodology.md` § Locators.
   Read the ids twice in separate commands — if they change, the framework re-renders and ids are
   worthless. Prefer `data-*` attributes, then ARIA roles, then text. Never key on generated ids.
4. **Configure the target.** Edit `scripts/config.sh`: URL, optional modal dismiss selector, the
   minimum fields to fill (`'selector :: value'`), the action selector, and a success pattern.
   Make the success pattern **specific** — a loose one matches unrelated page copy and will report
   a discarded action as a success.
5. **Probe at machine speed.** `bash scripts/probe.sh 0`. If the action lands, there is no race —
   report that and stop. If it is discarded, continue.
6. **Prove the site is at fault, not the tool.** `bash scripts/attribute.sh`. This attaches a
   capture-phase listener and hooks fetch/XHR, then clicks once and again. A first click that
   increments the listener but sends no request is a site defect. If the listener does not fire,
   the click missed — fix the locator and return to step 5.
7. **Bisect the window.** `bash scripts/bisect.sh` sweeps the pre-click delay and narrows the
   boundary to a bracket. Stop when the bracket is under ~500ms.
8. **Confirm both edges.** Re-run `probe.sh` twice at the last failing delay and twice at the first
   passing delay. The boundary is only real if it reproduces on both sides.
9. **Check who is affected.** A window under ~5s is reachable by autofill users and by fast
   returning visitors, not by anyone reading the form. State this in the report.
10. **Repeat the whole hunt in a fresh session** before believing it. Behavioural findings must
    reproduce; absolute timings will drift.

## Safety Boundaries

> [!IMPORTANT]
> Every probe performs a **real** action against the target — a real form submission, a real order,
> a real write. Before running anything:
> - Only ever run against sandboxes, staging, or systems the user owns. Never a third party's
>   production site.
> - Use obviously fake test data (`Test Testerson`, `test@example.invalid`). Never real customer data.
> - Keep the total probe count low. A full bisect is 8–12 actions; do not sweep in 100ms steps.
> - If the action is destructive or irreversible (payment, delete, publish, email send), stop and ask
>   the user before the first probe.
> - Do not modify the target site, only observe it.

> [!NOTE]
> Do not report a race until `attribute.sh` has confirmed the page received the click. An action that
> silently fails because the locator was wrong looks identical to one the page discarded.

## Output Format

Report findings under these headers:

- **Confirmed race** — the action, the measured window (`last failure → first success`), and the
  reproduction count on each side.
- **Attribution** — the listener and network evidence proving site over tool.
- **Who it reaches** — whether the window is short enough that only autofill or returning users hit
  it, or wide enough that ordinary visitors do.
- **Not reproduced** — probes that passed, so the reader knows what was ruled out.

Quote the window as a bracket between two measurements you actually took (`3.69–4.20s`), never as a
rounded single number. Never paint an unmeasured interval as confirmed in a chart or a claim.

## Files

- `scripts/config.sh` — the target definition; both scripts read it. Edit this, not the scripts.
- `scripts/probe.sh` — one attempt at a chosen delay; prints `SWALLOWED` or `worked`.
- `scripts/bisect.sh` — sweeps and narrows to the boundary bracket.
- `scripts/attribute.sh` — listener + network evidence, site vs tool.
- `references/methodology.md` — locator strategy, failure modes, and the reasoning behind the method.
