# candy-mapping

An agent skill for hunting **startup and hydration races** in web UIs — the class of defect where a
click lands before the page has finished wiring itself up and is silently discarded, with no error
and no request.

These bugs are invisible to manual testing and to slow agent-driven automation, and reproduce 100% of
the time to anything quick. This skill races the page, proves the site is at fault rather than the
tooling, and measures the exact window in which the page is vulnerable.

Named for the [CandyMapper](https://candymapper.com/) sandbox where the method was worked out.

## Install

```sh
npx skills add lana-20/candy-mapping -g
```

Or clone into your agent's skills directory:

```sh
git clone https://github.com/lana-20/candy-mapping.git ~/.claude/skills/candy-mapping
```

Requires the [Vibium](https://github.com/vibiumdev/vibium) CLI on `PATH` (or set `VIBIUM=/path/to/vibium`).

## Use

Ask your agent to candy-map a site, hunt race conditions, or investigate a button that "does nothing
on the first click". Or run the scripts directly:

```sh
# 1. point it at the target
$EDITOR scripts/config.sh

# 2. does the action land at machine speed?
bash scripts/probe.sh 0            # → SWALLOWED | worked

# 3. site defect or missed click?
bash scripts/attribute.sh          # listener + network evidence

# 4. how wide is the window?
bash scripts/bisect.sh             # narrows to a bracket
```

`attribute.sh` is the one that keeps you honest:

```
after click 1 → listener=1  network=[]
after click 2 → listener=2  network=["POST .../v3/messages"]
```

The page **received** the first click and chose to do nothing with it. That is a site defect. If the
listener never fires, the click missed the element and your locator is wrong — not a race.

## What it found

On the reference target, the window was originally measured at **3.7–4.2 seconds** after page
load — a click at 3,687ms discarded, one at 4,199ms through, reproducing on both sides. Hardened
2026-08-04: the boundary **drifts within a single session**, not just session to session — a
re-bisection ~30 minutes later found a zero-interaction control click still swallowed at 6,054ms.
Treat any published window as a snapshot, not a constant — see
[`references/timing-methodology.md`](references/timing-methodology.md).

Across sixty original benchmark runs the same eight steps were driven two ways, hardened
2026-08-04 to 100 independent runs of the full canonical journey:

| Driver | Reaches the action | Hit the bug (original, n=30) | Hit the bug (hardened, n=50) |
|---|---|---|---|
| Scripted CLI | ~1s originally, ~4.7s hardened median | **30 / 30** | **49 / 50** |
| Agent-driven MCP | ~25s originally, ~21.3s hardened median | **0 / 30** | **50 / 50** |

Same site, same selectors, same browser engine. Only arrival time differs — which is why a human
moving a mouse never sees it, and why the defect selects for your fastest users, the ones whose
browser autofills the form. The arrival-time *gap* shrank under harder replication (original ~25×,
hardened medians ~4.6×) even as the finding itself held — see
[`references/test-case.md`](references/test-case.md) for the exact 8-step sequence both arms now
run, and [`references/timing-methodology.md`](references/timing-methodology.md) for the full
hardened numbers, cost ($11.71, MCP arm), and two harness bugs the hardening pass caught along the
way.

The full write-up is [`index.html`](index.html) — read it at
**[lana-20.github.io/candy-mapping](https://lana-20.github.io/candy-mapping/)**. Companion
diagrams tracing what a CLI call and an MCP tool call actually do underneath:
[`vibium-cli-flow.html`](vibium-cli-flow.html) /
[`vibium-mcp-flow.html`](vibium-mcp-flow.html) — and the real command issued at each of the
8 canonical steps, side by side: [`vibium-test-case-commands.html`](vibium-test-case-commands.html).

## Safety

> [!IMPORTANT]
> Every probe performs a **real** action against the target — a real submission, a real write.
> Run only against sandboxes, staging, or systems you own. Use obviously fake test data. Keep probe
> counts low. If the action is destructive or irreversible, do not run this without thinking first.

## Layout

```
SKILL.md                          frontmatter, process steps, safety boundaries, output spec
scripts/config.sh                 target definition — the only file you edit
scripts/probe.sh                  one attempt at a chosen delay → SWALLOWED | worked
scripts/bisect.sh                 sweeps and narrows to the boundary bracket
scripts/attribute.sh              capture-phase listener + network hook: site vs tool
scripts/journey_cli.sh            full 8-step canonical journey, scripted (n-run batches)
scripts/journey_mcp.py            full 8-step canonical journey, agent-driven via MCP
references/methodology.md         locator strategy, failure modes, reporting standards
references/timing-methodology.md  the clock mechanism, its precision limits, the hardening pass
references/test-case.md           the exact 8-step canonical sequence, verbatim
references/selectors.md           full CandyMapper contact-form field map
references/session-isolation.md   CLI vs MCP concurrency: verified no state leak
data/runs/                        raw per-run JSON + transcripts from the hardening pass
index.html                        the article this came out of
vibium-cli-flow.html              diagram: what a CLI call does underneath
vibium-mcp-flow.html              diagram: what an MCP tool call does underneath
```

## Credit

The [sandbox](https://candymapper.com/) is [Paul Grossman's](https://www.linkedin.com/in/pmgrossman/),
and the speed grid reproduced in the article is his work. Thanks for building something genuinely
worth breaking tools against.
