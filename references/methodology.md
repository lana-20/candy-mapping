# Candy Mapping — methodology

Worked out against the CandyMapper pop-up challenge, July 2026. Sixty benchmark runs plus a
ten-point delay sweep produced the method below.

## Why fast automation finds what nothing else can

A startup race is not flaky. It is perfectly deterministic — the page is vulnerable for a fixed
interval after load, and whether you see the defect depends entirely on when your click arrives.

On the original hunt the same eight steps were driven two ways:

| Driver | Reaches the action | Hit the bug |
|---|---|---|
| Scripted CLI | ~1s after filling | 30 / 30 runs |
| Agent-driven MCP | ~25s after filling | 0 / 30 runs |

Same site, same selectors, same browser engine. A human reading labels and moving a mouse is firmly
in the second category, which is why these defects survive manual test cycles indefinitely.

The corollary matters for tool choice: if everything in a pipeline is slow, an entire category of
hydration and startup races sits outside its field of view. Keep something fast in the suite.

## Locators: the precondition

Frameworks that re-render hand out fresh element ids each time. On the reference target the ids were
sequential counters that changed *between two consecutive commands*:

```
ids        → ["input5878","input5879","input5880","input5881"]
is visible → true
fill       → element not found
ids        → ["input11","input12","input13","input14"]   ← renamed mid-instruction
```

Test for this before anything else — read the ids, run one interaction, read them again. If they
move, every id-based locator in the suite is a receipt for a node that no longer exists.

Preference order: `data-*` attributes the app ships → ARIA role plus accessible name → visible text →
structural CSS. Generated ids never.

This is also a product finding worth reporting, not just a testing inconvenience: analytics, session
replay, autofill heuristics and assistive-technology bindings all key on field identity too.

## Failure modes that will fool you

**An empty check is not evidence of absence.** The single largest error on the original hunt: a
success message was reported as "too transient to assert" when in fact it persists for over thirty
seconds. Every check that came back empty had run after a *discarded* click, so nothing had been
submitted and there was no message to find. The race was impersonating a rendering bug. Always
confirm the setup actually happened before drawing conclusions about the outcome.

**Two small errors that agree feel like one strong finding.** The same wrong conclusion was
reinforced by a regex that could not match the real wording. When two independent signals agree,
check that they are actually independent.

**A modal may only fire on a cold cache.** Clearing cookies does not clear the HTTP cache. The first
page load of a fresh browser is materially slower than subsequent ones — on the reference target,
~2.6s versus ~1.1s — so never compare a first run against later ones.

**Process spawn is not free but it is not the story either.** The CLI costs ~120ms per invocation.
Across a 27-command script that is ~3s, which is real but dwarfed by network and the site's own
response time. Do not over-optimise the harness before measuring where the time goes.

## Reporting standards

Quote the window as a bracket between two clicks you actually measured. On the reference target that
was a discard at 3,687ms and a success at 4,199ms, published as **3.7–4.2s** — the label rounds, the
evidence behind it does not. Never "about four seconds". If you draw it, the confirmed regions must end at real measurements and the untested
gap between them must be visually distinct (hatching works well). Painting an unmeasured interval as
confirmed is the easiest way to lose a reader who checks.

Run the whole hunt in a fresh session before publishing. Behavioural findings reproduce; absolute
timings drift. On the original work every behavioural finding held across three sessions while every
timing figure moved, one of them by 40%.

If a grid or benchmark tempts you to imply that other tools miss the bug — measure the window and
publish it as a self-check instead. A falsifiable threshold anyone can test in two minutes is a much
stronger position than an inference about someone else's product.

## Verify your own harness first

Both scripts in this skill shipped with a bug on their first run, and both were instances of the
very failure this method exists to catch. Worth repeating because they are easy to make:

**A loose success pattern reports failure as success.** `probe.sh` originally matched `thank you`
anywhere on the page, and the reference target happens to contain "thank you for listening to the
Test Guild podcast" in its footer. Every probe passed, including ones at zero delay that were
definitely discarded. Detection now requires text that was *absent before* the click and *present
after* it — and the configured pattern should be as specific as the real confirmation.

**An accepted selector is not a working selector.** The fill pairs were split on `=`, but the first
`=` sits inside `input[data-aid="First Name"]`, so the selector became `input[data-aid` and the value
became `"First Name"]=Test`. The driver accepted the malformed selector without error and wrote to
the wrong element. The form then failed validation, the submit did nothing, and the probe reported a
timing race that did not exist.

The general rule: **read back every precondition before measuring the outcome.** `probe.sh` now fills
each field and immediately reads its value, aborting with `PRECONDITION FAILED` if they disagree. A
half-filled form fails validation and is indistinguishable from a discarded click unless you check.
