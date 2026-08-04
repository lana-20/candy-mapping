#!/usr/bin/env python3
"""
Build the print-ready poster board: assets/poster-board.html

  python3 scripts/build_board.py [--landscape]

A0 at 1:1 — 841 x 1189 mm portrait (33.1 x 46.8 in), matching the official
PNSQC-2026-Poster-Template-Portrait.pptx trim size.

Fully static and self-contained (data + brand images inlined as base64) so
print engines don't need to run any script before paginating. Open in
Chrome, Print, "Save as PDF", paper A0, margins None, background graphics ON.
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from chart_lib import timeline_svg, grid_svg

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "assets" / "brand"
PHOTOS = ROOT / "assets" / "photos"
OUT = ROOT / "assets" / "poster-board.html"


def brand(name):
    p = BRAND / name
    if not p.exists():
        raise SystemExit(f"missing brand asset: {p}")
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


def photo(name):
    p = PHOTOS / name
    if not p.exists():
        raise SystemExit(f"missing photo asset: {p}")
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


def run_strip(hits, total, color):
    cells = "".join(
        f'<i class="c hit" style="background:{color}"></i>' if i < hits else '<i class="c miss"></i>'
        for i in range(total)
    )
    return f'<span class="cells">{cells}</span>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--landscape", action="store_true")
    args = ap.parse_args()
    W, H = (1189, 841) if args.landscape else (841, 1189)
    cols = 3 if not args.landscape else 4

    data_path = ROOT / "assets" / "poster_data.json"
    if not data_path.exists():
        raise SystemExit(f"missing {data_path.relative_to(ROOT)} — nothing to build from")
    data = json.loads(data_path.read_text())
    b = data["boundary"]
    hard = data["hardening"]
    # Run-strip and comparison panel now show the hardened n=70 data (2026-08-04), not
    # the original 30/30 — "hits" keeps its established meaning here, "hit the bug"
    # (SWALLOWED), for both arms.
    cli = {"hits": hard["cli"]["swallowed"], "total": hard["cli"]["n"]}
    mcp = {"hits": hard["mcp"]["swallowed"], "total": hard["mcp"]["n"]}
    grid = data["grid"]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Quality in the Age of Autonomy — PNSQC 2026</title>
<style>
@page {{ size: {W}mm {H}mm; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
:root {{
  --ground:#FBFBF9; --panel:#FFFFFF; --sunk:#F3F4F0;
  --ink:#141615; --ink2:#3C413B; --ink3:#6A706A;
  --rule:#DCDFD7; --rule2:#C3C7BC;
  --cli:#4a3aa7; --mcp:#eb6834; --bad:#d03b3b; --badbg:#FDF1F1;
  --sans: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono: ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}}
body {{
  width:{W}mm; height:{H}mm; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:8.4mm; line-height:1.42;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}}
.board {{ width:100%; height:100%; display:flex; flex-direction:column; }}
.brandbar {{ display:block; width:100%; height:auto; }}
.inner {{ flex:1 1 auto; padding:7mm 16mm 8mm; display:flex; flex-direction:column; gap:4mm; min-height:0; }}
.pnsqc-logo {{ width:26mm; height:26mm; flex:0 0 auto; }}

h1 {{ font-size:22mm; line-height:0.98; letter-spacing:-0.025em; font-weight:800; margin:2mm 0 3mm; }}
h2 {{ font-size:8.8mm; line-height:1.12; letter-spacing:-0.015em; font-weight:750; margin:0 0 3mm; }}
h3 {{ font-size:7.4mm; font-weight:700; margin:0 0 2mm; }}
p  {{ margin:0; }}
.kick {{ font-family:var(--mono); font-size:5.4mm; letter-spacing:0.18em; text-transform:uppercase;
        color:var(--cli); font-weight:700; }}
.q   {{ font-size:9mm; line-height:1.2; color:var(--ink3); font-weight:500; }}
.eyebrow {{ font-family:var(--mono); font-size:5mm; letter-spacing:0.15em; text-transform:uppercase;
           color:var(--ink3); font-weight:600; margin-bottom:2.5mm; }}
.small {{ font-size:6.3mm; color:var(--ink3); line-height:1.34; }}

header {{ border-bottom:1mm solid var(--ink); padding-bottom:3.5mm; }}
.hgrid {{ display:grid; grid-template-columns: 1fr 300mm; gap:14mm; align-items:end; }}
.figs {{ display:grid; grid-template-columns:repeat(2,1fr); gap:1px; background:var(--rule);
        border:1px solid var(--rule); }}
.fig {{ background:var(--ground); padding:3mm 4mm 3.5mm; }}
.figv {{ font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:12mm;
        font-weight:700; line-height:1; letter-spacing:-0.03em; }}
.figv.a {{ color:var(--cli); }} .figv.b {{ color:var(--bad); }}
.figl {{ font-size:5.6mm; color:var(--ink3); margin-top:2mm; line-height:1.3; }}
.byline {{ display:flex; flex-wrap:wrap; gap:1.5mm 9mm; margin-top:3.5mm;
          font-family:var(--mono); font-size:5.8mm; color:var(--ink3); }}
.byline b {{ color:var(--ink2); }}

.cols {{ display:grid; grid-template-columns:repeat({cols},1fr); gap:8mm; align-items:stretch; }}
.cols > .stack {{ height:100%; }}
.cols > .stack > :last-child {{ flex:1 1 auto; }}
.cols.grow {{ flex:1 1 auto; }}
.panel {{ background:var(--panel); border:0.5mm solid var(--rule); padding:4.6mm 5mm 5mm; }}
.panel.sunk {{ background:var(--sunk); }}
.panel.bad  {{ background:var(--badbg); border-color:var(--bad); }}
.stack {{ display:flex; flex-direction:column; gap:4mm; }}

.find {{ display:grid; grid-template-columns:8mm 1fr; gap:3mm; padding:2mm 0;
        border-top:0.4mm solid var(--rule); align-items:baseline; }}
.find:first-of-type {{ border-top:0; }}
.findk {{ font-family:var(--mono); font-size:5.6mm; font-weight:700; color:var(--cli); }}
.find.w .findk {{ color:var(--bad); }}
.find p {{ font-size:6.8mm; line-height:1.3; }}

.striphead {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:3mm; }}
.cells {{ display:flex; gap:0.7mm; flex-wrap:wrap; }}
.c {{ width:4.4mm; height:7mm; border-radius:0.7mm; background:#E4E7E0; position:relative; }}
.c.miss::after {{ content:""; position:absolute; inset:2.8mm 0.7mm; background:var(--rule2); border-radius:0.4mm; }}
.runrow {{ display:grid; grid-template-columns:44mm 1fr 30mm; gap:4mm; align-items:center; margin-bottom:3mm; }}
.runlab {{ font-family:var(--mono); font-size:5.8mm; color:var(--ink2); }}
.runrate {{ font-family:var(--mono); font-size:6.4mm; font-weight:700; text-align:right; }}

table {{ border-collapse:collapse; width:100%; font-size:6.4mm; }}
th,td {{ padding:1.7mm 3mm; text-align:left; border-bottom:0.4mm solid var(--rule); }}
thead th {{ font-family:var(--mono); font-size:5mm; letter-spacing:0.08em; text-transform:uppercase;
           color:var(--ink3); background:var(--sunk); }}
td.n, th.n {{ text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums; }}
tbody tr:last-child td {{ border-bottom:0; }}
ul {{ margin:0; padding-left:6mm; }}
li {{ font-size:6.4mm; color:var(--ink2); margin-bottom:1.5mm; line-height:1.3; }}
code {{ font-family:var(--mono); font-size:0.9em; }}
pre {{ font-family:var(--mono); font-size:5.6mm; background:var(--sunk); padding:3mm 3.5mm;
      border-radius:1mm; overflow:hidden; white-space:pre-wrap; line-height:1.5; color:var(--ink2); }}
.steps {{ counter-reset:s; }}
.step {{ display:grid; grid-template-columns:7mm 1fr; gap:3mm; margin-bottom:2.6mm; }}
.step::before {{ counter-increment:s; content:counter(s); font-family:var(--mono); font-size:5.4mm;
                font-weight:700; color:var(--cli); border:0.4mm solid var(--rule2); border-radius:50%;
                width:8mm; height:8mm; display:grid; place-items:center; }}
.step b {{ font-size:6.8mm; }} .step p {{ font-size:6.2mm; color:var(--ink3); line-height:1.32; }}
.tlwrap {{ background:var(--sunk); border-radius:1mm; padding:3mm; }}
figure {{ margin:0; }}
figure img {{ display:block; width:100%; border:0.4mm solid var(--rule); }}
figcaption {{ font-size:5.6mm; color:var(--ink3); margin-top:2mm; line-height:1.3; }}
figcaption b {{ color:var(--ink2); }}
footer {{ margin-top:auto; border-top:0.8mm solid var(--ink); padding-top:5mm;
         display:flex; justify-content:space-between; gap:10mm; font-size:6mm; color:var(--ink3); }}
footer b {{ color:var(--ink); }}
</style></head>
<body><div class="board">
<img class="brandbar" src="{brand('pnsqc-banner.jpg')}" alt="44th Annual Pacific NW Software Quality Conference — Quality in the Age of Autonomy — October 12-14, 2026 — pnsqc.org">
<div class="inner">

<header>
  <div class="hgrid">
    <div>
      <p class="kick">Poster &middot; PNSQC 2026</p>
      <p class="q">How fast do you have to be to see a bug whose hiding window keeps moving?</p>
      <h1>Quality in the age of autonomy:<br>deliberation costs you the bug.</h1>
      <div class="byline">
        <span><b>Lana Begunova</b> &middot; Daisy Lady Bug &middot; begunova@gmail.com</span>
        <span>AUT <b>candymapper.com</b></span>
        <span>Tool <b>Vibium v26.5.31</b> &middot; CLI + MCP surfaces</span>
        <span><b>{data['date']}</b> &middot; {data['sessions']} sessions</span>
      </div>
    </div>
    <div class="figs">
      <div class="fig"><div class="figv a">3.7&ndash;4.4s</div><div class="figl">vulnerability window<br>moves within a session &mdash; not fixed</div></div>
      <div class="fig"><div class="figv b">69/70 &middot; 70/70</div><div class="figl">hardened hit rate, n=70 each<br>2026-08-04, full 8-step journey</div></div>
      <div class="fig"><div class="figv">200</div><div class="figl">total benchmark runs<br>60 original + 140 hardening</div></div>
      <div class="fig"><div class="figv b">4.7&times;</div><div class="figl">slower arrival at Submit, hardened<br>22.0s (MCP) vs 4.7s (CLI) medians</div></div>
    </div>
  </div>
</header>

<div class="cols">
  <div class="panel sunk">
    <p class="eyebrow">Conclusions</p>
    <h2>What the window showed, then what hardening it showed</h2>
    <div class="find"><span class="findk">01</span><p><b>The Submit button is clickable before its own handler
      finishes wiring up.</b> The first click after load lands and is silently discarded &mdash; no error,
      no request, nothing to notice. Click again and it works.</p></div>
    <div class="find"><span class="findk">02</span><p><b>Proven a site defect, not a tool artefact.</b> A
      capture-phase listener plus a network hook show the click was received and then ignored; a bare
      <code>element.click()</code> in the console reproduces it.</p></div>
    <div class="find w"><span class="findk">03</span><p><b>The boundary drifts within a single session,
      not just session to session.</b> Three real bisections, same session: 3,687&rarr;4,199ms,
      then 3,941&rarr;4,252ms ~45min later, then 4,095&rarr;4,393ms ~90min later &mdash; a consistent
      150&ndash;250ms creep each time. Quote a range measured close to publication, never a fixed
      constant.</p></div>
    <div class="find w"><span class="findk">04</span><p><b>Hardened at n=70 each, the finding holds &mdash;
      the margin doesn't.</b> CLI's median arrival rose to ~4.7s (up from ~1s), landing much closer to
      the boundary than originally measured; MCP stayed ~22s. 69/70 CLI runs still hit the bug, 70/70
      MCP runs still avoided it &mdash; but the 25&times; arrival gap first measured is really ~4.7&times;
      under harder, more complete replication (full 8-step journey, not a 2-field shortcut).</p></div>
    <div class="find"><span class="findk">05</span><p><b>The negative path is raced too.</b> Submitting
      without an email is supposed to show a validation error before the real submit. For CLI it almost
      never does (0/70) &mdash; that click is fast enough to be swallowed by the same race. For MCP it
      always does (70/70) &mdash; the agent's own reasoning time carries it past the window by then.</p></div>
    <div class="find"><span class="findk">06</span><p><b>A human tester falls in the slow category
      too.</b> Moving a mouse and reading labels takes far longer than the window stays open &mdash; this
      defect is structurally invisible to manual testing regardless of which measurement of the window
      you use.</p></div>
    <div class="find"><span class="findk">07</span><p><b>It selects for your fastest users</b> &mdash;
      the ones whose browser autofills the form and clicks Submit almost immediately.</p></div>
  </div>

  <div class="stack">
    <div class="panel">
      <p class="eyebrow">Proof</p>
      <h2>Site fault, not a missed click</h2>
      <p class="small" style="margin-bottom:3mm">A capture-phase click listener plus a network hook,
        one click apart:</p>
      <pre>after click 1 &rarr; listener=1  xhr=[]  message=false
after click 2 &rarr; listener=2  xhr=["POST .../v3/messages"]</pre>
      <p class="small" style="margin-top:3mm">The page <b>received</b> the first click &mdash; the
        counter incremented &mdash; and did nothing with it. If the listener never fires, that's a
        locator problem, not a race. Here it always fires.</p>
    </div>
    <div class="panel bad">
      <h3>Not a defect, but costs you a day</h3>
      <ul>
        <li>Field ids regenerate on rebuild (<code>input5878</code> &rarr; <code>input11</code>);
          key on <code>data-aid</code> instead.</li>
        <li>Popup only fires on a cold cache &mdash; clear cookies first.</li>
        <li>Only first name + email are enforced; phone and message are optional despite the SMS notice.</li>
      </ul>
    </div>
  </div>

  <div class="stack">
    <figure>
      <img src="{photo('hero.jpg')}" alt="A wrapped candy falling through a trapdoor in a checkered floor, caught mid-fall in the window before the page is ready.">
      <figcaption><b>CandyMapper.com</b> &mdash; Paul Grossman's "Website That Goes Wrong," wrapping a
        contact-form journey around eleven planted defects and eight hidden references.</figcaption>
    </figure>
    <div class="panel sunk">
      <p class="eyebrow">Method</p>
      <div class="steps">
        <div class="step"><div><b>probe</b><p>One timed attempt at a chosen delay &rarr; SWALLOWED or worked.</p></div></div>
        <div class="step"><div><b>attribute</b><p>Capture-phase listener + network hook: proves site
          fault vs missed click.</p></div></div>
        <div class="step"><div><b>bisect</b><p>Sweep the delay, narrow to the failure boundary.</p></div></div>
      </div>
    </div>
  </div>
</div>

<div class="panel">
  <div class="striphead">
    <div>
      <p class="eyebrow">Result &mdash; the boundary (original measurement)</p>
      <h2>Ten probes, one sharp edge &mdash; then it moved</h2>
    </div>
    <p class="small" style="max-width:330mm; text-align:right"><b style="color:var(--bad)">Red = swallowed.</b>
      <b style="color:var(--cli)">Purple = worked.</b> Callout marks the {data['date']} boundary. Confirmed
      2026-08-04 this is a snapshot, not a constant &mdash; see below.</p>
  </div>
  <div class="tlwrap">{timeline_svg(data['bisect'], b, w=1300, h=440)}</div>
</div>

<div class="panel">
  <div class="striphead">
    <div>
      <p class="eyebrow">Result &mdash; where Vibium lands on the community grid</p>
      <h2>Fastest run time on Paul Grossman's own speed grid</h2>
    </div>
    <p class="small" style="max-width:330mm; text-align:right">16 published tools (grey) plus Vibium's two
      entries. Bars show the MCP arm's wide build/setup-vs-run range &mdash; its "zero build time"
      just moves the authoring cost into every run.</p>
  </div>
  <div class="cols" style="grid-template-columns:1fr 2fr; gap:9mm; align-items:start">
    <figure>
      <img src="{photo('grossman-grid.jpg')}" alt="Paul Grossman's original CandyMapper Challenge 2026 speed grid, sixteen tools plotted by build time against run time.">
      <figcaption>The grid <b>as Paul published it</b> &mdash; 16 tools, build time (minutes) vs run
        time (seconds), four quadrants.</figcaption>
    </figure>
    <div>
      <div class="tlwrap">{grid_svg(grid)}</div>
      <p class="small" style="margin-top:2mm"><b>Vibium CLI</b> lands in Speedsters at 8.9s run time,
        fastest on the whole grid. <b>Vibium MCP</b> has no authored script &mdash; that cost is paid
        every run instead, 49.5&ndash;69.4s.</p>
    </div>
  </div>
</div>

<div class="cols grow" style="grid-template-columns:repeat(2,1fr)">
  <div class="stack">
    <div class="panel">
      <p class="eyebrow">Result &mdash; the comparison</p>
      <h2>Same site. Only arrival time differs.</h2>
      <p class="small" style="margin-bottom:3mm">Vibium is the verification layer for
        coding agents &mdash; the CLI and the MCP server are two surfaces onto the same
        daemon and browser. Same click, same tool underneath; only how the caller reaches
        it differs.</p>
      <div class="runrow">
        <span class="runlab">CLI &middot; ~4.7s to Submit</span>
        {run_strip(cli['hits'], cli['total'], 'var(--cli)')}
        <span class="runrate" style="color:var(--cli)">{cli['hits']}/{cli['total']}</span>
      </div>
      <div class="runrow">
        <span class="runlab">MCP &middot; ~22.0s to Submit</span>
        {run_strip(mcp['hits'], mcp['total'], 'var(--bad)')}
        <span class="runrate" style="color:var(--bad)">{mcp['hits']}/{mcp['total']}</span>
      </div>
      <p class="small" style="margin-top:2mm">Hardened n=70 each, 2026-08-04, full 8-step canonical
        journey. Same selectors, same browser build. Nothing about the agent's judgment was at fault
        &mdash; it simply arrived too late, every time. (1 CLI run excluded: a precondition failure,
        not counted either way.)</p>
      <p class="small" style="margin-top:2mm"><b>Why MCP is slower:</b> not the browser &mdash; both
        arms pay the same ~170&ndash;250ms per actual action underneath. The CLI script issues all
        8 steps back to back with no thinking between them. The MCP agent re-reasons at every one of
        those 8 steps &mdash; reads the last result, decides the next tool call, then calls it &mdash;
        so the gap is 8 stacked reasoning turns, not one slow step.</p>
    </div>
    <div class="panel">
      <p class="eyebrow">Result &mdash; the fix</p>
      <h2>Rebuild-proof locators</h2>
      <pre>fill 'input[data-aid="First Name"]'          "Lana"
fill 'input[data-aid="CONTACT_FORM_EMAIL"]' "lana@daisyladybug.com"
click 'button[data-aid="CONTACT_SUBMIT_BUTTON_REND"]'</pre>
      <p class="small" style="margin-top:2mm">Switching from generated ids to <code>data-aid</code>
        took the suite from intermittently green to 100%.</p>
    </div>
  </div>

  <div class="stack">
    <div class="panel">
      <p class="eyebrow">Try it yourself</p>
      <h2>A two-minute self-check</h2>
      <table>
        <tbody>
          <tr><td class="n">1</td><td>Load the page cold, dismiss the modal.</td></tr>
          <tr><td class="n">2</td><td>Fill first name + email only.</td></tr>
          <tr><td class="n">3</td><td>Click Submit under 4s after load.</td></tr>
          <tr><td class="n">4</td><td>Watch the network &mdash; no request means the click was
            discarded. Click again and it fires.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="panel sunk">
      <p class="eyebrow">Take this home</p>
      <ul>
        <li><b>Test speed is an aperture</b>, not a CI cost line &mdash; it decides which hydration
          races a suite can even perceive.</li>
        <li><b>Deliberation has a cost</b> a slower, more careful agent structurally cannot see this
          class of bug.</li>
        <li><b>Never key locators on generated ids.</b></li>
        <li><b>Assert the negative path</b>, not only the happy one.</li>
        <li><b>Run everything at least three times</b> before you believe your own findings.</li>
      </ul>
    </div>
  </div>
</div>

<footer>
  <p><b>Disclosure.</b> Per the PNSQC Generative AI Policy. Tool: Vibium v26.5.31 (CLI + MCP), model
    claude-sonnet-5 driving the agentic arm; AI also assisted drafting and script authoring. Every
    figure reproduced from published scripts and raw run logs. Method: an eight-step contact-form
    journey. Original measurement 60 runs across 3 sessions, {data['date']}, 480/480 steps passing.
    Hardened 2026-08-04 with 70 CLI + 70 MCP independent runs of the full journey. Full write-up
    and repro scripts at github.com/lana-20/candy-mapping. Thanks to Paul
    Grossman for building CandyMapper.com and for publishing the speed grid reproduced above,
    sandboxes and data genuinely worth breaking (and reusing) tools against. The author is
    accountable for every claim.</p>
  <div style="display:flex; gap:6mm; align-items:flex-start">
    <p style="text-align:right; white-space:nowrap"><b>Lana Begunova</b><br>begunova@gmail.com<br>
      github.com/lana-20/candy-mapping<br>daisyladybug.com</p>
    <img class="pnsqc-logo" src="{brand('pnsqc-logo.jpg')}" alt="PNSQC 2026">
  </div>
</footer>

</div>
</div></body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(ROOT)}  ({kb:.0f} KB) — {W}x{H} mm "
          f"({W/25.4:.1f}x{H/25.4:.1f} in), self-contained")
    print("  print: Chrome -> Print -> Save as PDF -> paper A0, margins None, background graphics ON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
