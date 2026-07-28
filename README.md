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

On the reference target, the window is **3.7–4.2 seconds** after page load, and the boundary is
sharp: a click at 3,687ms is discarded, one at 4,199ms goes through, reproducing on both sides.

Across sixty benchmark runs the same eight steps were driven two ways:

| Driver | Reaches the action | Hit the bug |
|---|---|---|
| Scripted CLI | ~1s after filling | **30 / 30** |
| Agent-driven MCP | ~25s after filling | **0 / 30** |

Same site, same selectors, same browser engine. Only arrival time differs — which is why a human
moving a mouse never sees it, and why the defect selects for your fastest users, the ones whose
browser autofills the form.

The full write-up is [`index.html`](index.html) — read it at
**[lana-20.github.io/candy-mapping](https://lana-20.github.io/candy-mapping/)**.

## Safety

> [!IMPORTANT]
> Every probe performs a **real** action against the target — a real submission, a real write.
> Run only against sandboxes, staging, or systems you own. Use obviously fake test data. Keep probe
> counts low. If the action is destructive or irreversible, do not run this without thinking first.

## Layout

```
SKILL.md                  frontmatter, process steps, safety boundaries, output spec
scripts/config.sh         target definition — the only file you edit
scripts/probe.sh          one attempt at a chosen delay → SWALLOWED | worked
scripts/bisect.sh         sweeps and narrows to the boundary bracket
scripts/attribute.sh      capture-phase listener + network hook: site vs tool
references/methodology.md locator strategy, failure modes, reporting standards
index.html                the article this came out of
```

## Credit

The [sandbox](https://candymapper.com/) is [Paul Grossman's](https://www.linkedin.com/in/pmgrossman/),
and the speed grid reproduced in the article is his work. Thanks for building something genuinely
worth breaking tools against.
