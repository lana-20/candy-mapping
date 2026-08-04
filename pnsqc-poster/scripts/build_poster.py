#!/usr/bin/env python3
"""
Build the scrollable web companion: assets/poster.html

  python3 scripts/build_poster.py

Responsive, light/dark aware, self-contained. Same data source as
build_board.py so the two never drift. Adds one interactive element the
print board can't: a draggable click-delay slider against the boundary.
"""

import base64
import json
import sys
from pathlib import Path

from chart_lib import timeline_svg, grid_svg

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "assets" / "photos"
OUT = ROOT / "assets" / "poster.html"


def photo(name):
    p = PHOTOS / name
    if not p.exists():
        raise SystemExit(f"missing photo asset: {p}")
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    data_path = ROOT / "assets" / "poster_data.json"
    if not data_path.exists():
        print(f"missing {data_path.relative_to(ROOT)} — nothing to build from")
        return 1
    data = json.loads(data_path.read_text())
    bisect_json = json.dumps(data["bisect"])
    boundary = data["boundary"]
    hard = data["hardening"]
    # Hardened n=50 data (2026-08-04), not the original 30/30 — "hits" keeps its
    # established meaning, "hit the bug" (SWALLOWED), for both arms.
    cli = {"hits": hard["cli"]["swallowed"], "total": hard["cli"]["n"]}
    mcp = {"hits": hard["mcp"]["swallowed"], "total": hard["mcp"]["n"]}
    grid = data["grid"]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Window Is Four Seconds Wide — candy-mapping — PNSQC 2026</title>
<style>
:root {{
  --ground:#FBFBF9; --panel:#FFFFFF; --sunk:#F3F4F0;
  --ink:#141615; --ink2:#3C413B; --ink3:#6A706A;
  --rule:#DCDFD7; --rule2:#C3C7BC;
  --cli:#4a3aa7; --mcp:#eb6834; --bad:#d03b3b; --badbg:#FDF1F1;
  --sans: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono: ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --ground:#15171A; --panel:#1B1E22; --sunk:#20242A; --ink:#EDEFEA; --ink2:#C7CBC4;
          --ink3:#8B9089; --rule:#33383E; --rule2:#454B52; --badbg:#2A1818; }}
}}
:root[data-theme="dark"] {{ --ground:#15171A; --panel:#1B1E22; --sunk:#20242A; --ink:#EDEFEA;
  --ink2:#C7CBC4; --ink3:#8B9089; --rule:#33383E; --rule2:#454B52; --badbg:#2A1818; }}
:root[data-theme="light"] {{ --ground:#FBFBF9; --panel:#FFFFFF; --sunk:#F3F4F0; --ink:#141615;
  --ink2:#3C413B; --ink3:#6A706A; --rule:#DCDFD7; --rule2:#C3C7BC; --badbg:#FDF1F1; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink); font-family:var(--sans);
       line-height:1.5; }}
img {{ max-width:100%; }}
.wrap {{ max-width:1000px; margin:0 auto; padding:0 20px 80px; }}
.kicker {{ font-family:var(--mono); font-size:12px; letter-spacing:0.14em; text-transform:uppercase;
          color:var(--ink3); padding-top:20px; }}
.kick {{ font-family:var(--mono); font-size:12px; letter-spacing:0.14em; text-transform:uppercase;
        color:var(--cli); font-weight:700; margin-top:10px; }}
.q {{ font-size:20px; color:var(--ink3); font-weight:500; margin:10px 0 6px; }}
h1 {{ font-size:clamp(32px,5vw,52px); line-height:1.02; letter-spacing:-0.02em; font-weight:800;
     margin:0 0 14px; }}
h2 {{ font-size:22px; font-weight:750; letter-spacing:-0.01em; margin:0 0 10px; }}
h3 {{ font-size:17px; font-weight:700; margin:0 0 8px; }}
.byline {{ display:flex; flex-wrap:wrap; gap:4px 20px; font-family:var(--mono); font-size:13px;
          color:var(--ink3); margin:14px 0 26px; }}
.byline b {{ color:var(--ink2); }}
.eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:0.12em; text-transform:uppercase;
           color:var(--ink3); font-weight:600; margin-bottom:8px; }}
.figs {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1px;
        background:var(--rule); border:1px solid var(--rule); margin-bottom:30px; }}
.fig {{ background:var(--panel); padding:16px 18px; }}
.figv {{ font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:30px; font-weight:700;
        letter-spacing:-0.02em; }}
.figv.a {{ color:var(--cli); }} .figv.b {{ color:var(--bad); }}
.figl {{ font-size:13px; color:var(--ink3); margin-top:6px; line-height:1.35; }}
.panel {{ background:var(--panel); border:1px solid var(--rule); border-radius:10px; padding:20px 22px;
         margin-bottom:18px; }}
.panel.sunk {{ background:var(--sunk); }}
.panel.bad {{ background:var(--badbg); border-color:var(--bad); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
@media (max-width:720px) {{ .grid2 {{ grid-template-columns:1fr; }} .figs {{ grid-template-columns:repeat(2,1fr); }} }}
.find {{ display:grid; grid-template-columns:26px 1fr; gap:10px; padding:9px 0;
        border-top:1px solid var(--rule); }}
.find:first-of-type {{ border-top:0; }}
.findk {{ font-family:var(--mono); font-size:13px; font-weight:700; color:var(--cli); }}
.find.w .findk {{ color:var(--bad); }}
.find p {{ margin:0; font-size:14.5px; line-height:1.42; }}
pre {{ font-family:var(--mono); font-size:13px; background:var(--sunk); padding:12px 14px;
      border-radius:8px; overflow-x:auto; line-height:1.5; color:var(--ink2); }}
.small {{ font-size:13.5px; color:var(--ink3); line-height:1.4; }}
code {{ font-family:var(--mono); font-size:0.92em; }}
ul {{ margin:0; padding-left:20px; }} li {{ margin-bottom:5px; font-size:14px; color:var(--ink2); }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th,td {{ padding:7px 10px; text-align:left; border-bottom:1px solid var(--rule); }}
thead th {{ font-family:var(--mono); font-size:11px; letter-spacing:0.06em; text-transform:uppercase;
           color:var(--ink3); background:var(--sunk); }}
.runrow {{ display:grid; grid-template-columns:150px 1fr 60px; gap:10px; align-items:center; margin-bottom:12px; }}
.runlab {{ font-family:var(--mono); font-size:12.5px; color:var(--ink2); }}
.cells {{ display:flex; gap:1.5px; flex-wrap:wrap; }}
.c {{ width:9px; height:16px; border-radius:2px; background:#E4E7E0; }}
.runrate {{ font-family:var(--mono); font-size:15px; font-weight:700; text-align:right; }}
.steps {{ counter-reset:s; }}
.step {{ display:grid; grid-template-columns:26px 1fr; gap:10px; margin-bottom:12px; }}
.step::before {{ counter-increment:s; content:counter(s); font-family:var(--mono); font-size:12px;
                font-weight:700; color:var(--cli); border:1px solid var(--rule2); border-radius:50%;
                width:22px; height:22px; display:grid; place-items:center; }}
.step b {{ font-size:14.5px; }} .step p {{ margin:2px 0 0; font-size:13.5px; color:var(--ink3); }}

.demo {{ background:var(--sunk); border:1px solid var(--rule); border-radius:10px; padding:20px 22px 22px; }}
#dot {{ font-family:var(--mono); font-size:15px; font-weight:700; padding:3px 10px; border-radius:5px;
       display:inline-block; margin-left:10px; }}
#dot.worked {{ color:var(--cli); background:color-mix(in srgb, var(--cli) 15%, transparent); }}
#dot.swallowed {{ color:var(--bad); background:color-mix(in srgb, var(--bad) 15%, transparent); }}
#slider {{ width:100%; margin:16px 0 6px; accent-color:var(--cli); }}
.slabels {{ display:flex; justify-content:space-between; font-family:var(--mono); font-size:11px;
           color:var(--ink3); }}
#band {{ position:relative; height:8px; background:var(--rule); border-radius:4px; margin:14px 0 4px; overflow:hidden; }}
#band .zone {{ position:absolute; top:0; bottom:0; background:var(--bad); opacity:0.35; }}
footer {{ margin-top:34px; border-top:2px solid var(--ink); padding-top:18px; font-size:12.5px;
         color:var(--ink3); display:flex; flex-wrap:wrap; gap:16px 40px; justify-content:space-between; }}
footer b {{ color:var(--ink); }}
figure {{ margin:0; }}
figure img {{ display:block; width:100%; border-radius:8px; border:1px solid var(--rule); }}
figcaption {{ font-size:12.5px; color:var(--ink3); margin-top:8px; line-height:1.4; }}
figcaption b {{ color:var(--ink2); }}
.chartbox {{ background:var(--sunk); border-radius:8px; padding:10px; }}
.themebtn {{ position:fixed; top:14px; right:14px; z-index:10; font-family:var(--mono); font-size:11px;
            padding:6px 10px; border-radius:6px; border:1px solid var(--rule2); background:var(--panel);
            color:var(--ink2); cursor:pointer; }}
</style></head>
<body>
<button class="themebtn" onclick="toggleTheme()">theme</button>
<div class="wrap">

<p class="kicker">PNSQC 2026 &middot; Poster companion</p>
<p class="kick">Quality in the Age of Autonomy</p>
<p class="q">How fast do you have to be to see a bug whose hiding window keeps moving?</p>
<h1>The window is four seconds wide.</h1>
<div class="byline">
  <span><b>Lana Begunova</b> &middot; Daisy Lady Bug &middot; begunova@gmail.com</span>
  <span>AUT <b>candymapper.com</b></span>
  <span>Tool <b>Vibium v26.5.31</b> &middot; CLI + MCP</span>
  <span><b>{data['date']}</b> &middot; {data['sessions']} sessions &middot; hardened 2026-08-04</span>
</div>

<div class="figs">
  <div class="fig"><div class="figv a">3.7&ndash;4.4s</div><div class="figl">vulnerability window, moves within a session</div></div>
  <div class="fig"><div class="figv b">49/50 &middot; 50/50</div><div class="figl">hardened hit rate, n=50 each</div></div>
  <div class="fig"><div class="figv">160</div><div class="figl">total runs, 60 original + 100 hardening</div></div>
  <div class="fig"><div class="figv b">4.6&times;</div><div class="figl">slower arrival, hardened medians</div></div>
</div>

<div class="panel sunk">
  <p class="eyebrow">Conclusions</p>
  <h2>What the window showed, then what hardening it showed</h2>
  <div class="find"><span class="findk">01</span><p><b>The Submit button is clickable before its own
    handler finishes wiring up.</b> The first click after load lands and is silently discarded &mdash;
    no error, no request. Click again and it works.</p></div>
  <div class="find"><span class="findk">02</span><p><b>Proven a site defect, not a tool artefact</b>
    &mdash; a capture-phase listener plus a network hook show the click was received and ignored; a
    bare <code>element.click()</code> reproduces it.</p></div>
  <div class="find w"><span class="findk">03</span><p><b>The boundary drifts within a single session,
    not just session to session.</b> Three real bisections, same session: 3,687&rarr;4,199ms, then
    3,941&rarr;4,252ms ~45min later, then 4,095&rarr;4,393ms ~90min later &mdash; a consistent
    150&ndash;250ms creep each time.</p></div>
  <div class="find w"><span class="findk">04</span><p><b>Hardened at n=50 each, the finding holds
    &mdash; the margin doesn't.</b> CLI's median arrival rose to ~4.7s (from ~1s originally), much
    closer to the boundary; MCP stayed ~21s. 49/50 CLI hit the bug, 50/50 MCP avoided it &mdash; but
    the 25&times; arrival gap first measured is really ~4.6&times; under full replication.</p></div>
  <div class="find"><span class="findk">05</span><p><b>The negative path is raced too.</b> Submitting
    without an email should show a validation error before the real submit. CLI almost never confirms
    it (0/50) &mdash; that click is fast enough to be swallowed by the same race. MCP always does
    (50/50) &mdash; its own reasoning time carries it past the window by then.</p></div>
  <div class="find"><span class="findk">06</span><p><b>A human tester falls in the slow category
    too</b> &mdash; this defect is structurally invisible to manual testing.</p></div>
  <div class="find"><span class="findk">07</span><p><b>It selects for your fastest users</b> &mdash;
    the ones whose browser autofills the form and clicks Submit almost immediately.</p></div>
</div>

<div class="panel">
  <p class="eyebrow">Result &mdash; the boundary (original measurement)</p>
  <h2>Ten probes, one sharp edge &mdash; then it moved</h2>
  <div class="chartbox">{timeline_svg(data['bisect'], boundary, w=900, h=440)}</div>
  <p class="small" style="margin-top:8px">Confirmed 2026-08-04 this is a snapshot, not a constant
    &mdash; see the conclusions above.</p>
</div>

<div class="demo">
  <p class="eyebrow">Try the boundary yourself</p>
  <h2>Drag the delay, watch the outcome flip</h2>
  <p class="small">This replays the ten measured probes against the real boundary
    ({boundary['discard_ms']}ms discard &rarr; {boundary['success_ms']}ms success). It is not live
    against CandyMapper &mdash; it is the recorded data, made draggable.</p>
  <div id="band"></div>
  <input id="slider" type="range" min="1000" max="25000" value="1000" step="1">
  <div class="slabels"><span>1.0s</span><span>25.0s</span></div>
  <p style="margin-top:10px; font-size:14px">Click delay: <span id="msval" style="font-family:var(--mono); font-weight:700">1000ms</span>
    &rarr; <span id="dot" class="swallowed">SWALLOWED</span></p>
</div>

<div class="grid2" style="margin-top:18px">
  <div class="panel">
    <p class="eyebrow">Proof</p>
    <h3>Site fault, not a missed click</h3>
    <pre>after click 1 &rarr; listener=1  xhr=[]  message=false
after click 2 &rarr; listener=2  xhr=["POST .../v3/messages"]</pre>
    <p class="small">The page <b>received</b> the first click &mdash; the counter incremented &mdash;
      and did nothing with it.</p>
  </div>
  <div class="panel bad">
    <h3>Not a defect, but costs you a day</h3>
    <ul>
      <li>Field ids regenerate on rebuild; key on <code>data-aid</code> instead.</li>
      <li>Popup only fires on a cold cache &mdash; clear cookies first.</li>
      <li>Only first name + email are enforced.</li>
    </ul>
  </div>
</div>

<div class="panel">
  <p class="eyebrow">Result &mdash; the comparison</p>
  <h2>Same site. Only arrival time differs.</h2>
  <p class="small" style="margin-bottom:10px">Hardened n=50 each, 2026-08-04, full 8-step canonical
    journey. (1 CLI run excluded: a precondition failure, not counted either way.)</p>
  <div class="runrow">
    <span class="runlab">CLI &middot; ~4.7s to Submit</span>
    <span class="cells">{''.join(f'<i class="c" style="background:var(--cli)"></i>' for _ in range(cli['hits']))}{''.join('<i class="c"></i>' for _ in range(cli['total']-cli['hits']))}</span>
    <span class="runrate" style="color:var(--cli)">{cli['hits']}/{cli['total']}</span>
  </div>
  <div class="runrow">
    <span class="runlab">MCP &middot; ~21.3s to Submit</span>
    <span class="cells">{''.join(f'<i class="c" style="background:var(--bad)"></i>' for _ in range(mcp['hits']))}{''.join('<i class="c"></i>' for _ in range(mcp['total']-mcp['hits']))}</span>
    <span class="runrate" style="color:var(--bad)">{mcp['hits']}/{mcp['total']}</span>
  </div>
  <p class="small">Same selectors, same browser build. Nothing about the agent's judgment was at
    fault &mdash; it simply arrived too late, every time.</p>
</div>

<div class="panel">
  <p class="eyebrow">Result &mdash; where Vibium lands on the community grid</p>
  <h2>Fastest run time on Paul Grossman's own speed grid</h2>
  <div class="grid2" style="align-items:start">
    <figure>
      <img src="{photo('grossman-grid-web.jpg')}" alt="Paul Grossman's original CandyMapper Challenge 2026 speed grid, sixteen tools plotted by build time against run time.">
      <figcaption>The grid <b>as Paul published it</b> &mdash; 16 tools, build time (minutes) vs run
        time (seconds).</figcaption>
    </figure>
    <div class="chartbox">{grid_svg(grid, w=560, h=320)}</div>
  </div>
  <p class="small" style="margin-top:10px"><b>Vibium CLI</b> lands in Speedsters at 8.9s run time,
    fastest on the whole grid. <b>Vibium MCP</b> has no authored script &mdash; that cost is paid every
    run instead, 49.5&ndash;69.4s.</p>
</div>

<div class="grid2">
  <figure>
    <img src="{photo('hero-web.jpg')}" alt="A wrapped candy falling through a trapdoor in a checkered floor, caught mid-fall in the window before the page is ready.">
    <figcaption><b>CandyMapper.com</b> &mdash; Paul Grossman's "Website That Goes Wrong," wrapping a
      contact-form journey around eleven planted defects and eight hidden references.</figcaption>
  </figure>
  <div class="panel sunk">
    <p class="eyebrow">Method</p>
    <div class="steps">
      <div class="step"><div><b>probe</b><p>One timed attempt &rarr; SWALLOWED or worked.</p></div></div>
      <div class="step"><div><b>attribute</b><p>Listener + network hook: site fault vs missed click.</p></div></div>
      <div class="step"><div><b>bisect</b><p>Sweep the delay, narrow to the boundary.</p></div></div>
    </div>
  </div>
</div>

<div class="panel">
  <p class="eyebrow">Try it yourself</p>
  <h2>A two-minute self-check</h2>
  <table>
    <tbody>
      <tr><td>1</td><td>Load the page cold, dismiss the modal.</td></tr>
      <tr><td>2</td><td>Fill first name + email only.</td></tr>
      <tr><td>3</td><td>Click Submit under 4s after load.</td></tr>
      <tr><td>4</td><td>Watch the network &mdash; no request means the click was discarded. Click
        again and it fires.</td></tr>
    </tbody>
  </table>
</div>

<div class="panel sunk">
  <p class="eyebrow">Take this home</p>
  <ul>
    <li><b>Test speed is an aperture</b>, not a CI cost line &mdash; it decides which hydration races
      a suite can even perceive.</li>
    <li><b>Deliberation has a cost</b> &mdash; a slower, more careful agent structurally cannot see
      this class of bug.</li>
    <li><b>Never key locators on generated ids.</b></li>
    <li><b>Assert the negative path</b>, not only the happy one.</li>
    <li><b>Run everything at least three times</b> before you believe your own findings.</li>
  </ul>
</div>

<footer>
  <p style="flex:2; min-width:260px"><b>Disclosure.</b> Per the PNSQC Generative AI Policy. Tool:
    Vibium v26.5.31 (CLI + MCP), model claude-sonnet-5 driving the agentic arm; AI also assisted
    drafting and script authoring. Method: an eight-step contact-form journey. Original measurement
    60 runs across 3 sessions, {data['date']}, 480/480 steps passing. Hardened 2026-08-04 with
    50 CLI + 50 MCP independent runs of the full journey (real cost $11.71, MCP arm). Full write-up
    and repro scripts at github.com/lana-20/candy-mapping. Thanks to Paul Grossman for building
    CandyMapper.com and publishing the speed grid reproduced above.</p>
  <p><b>Lana Begunova</b><br>begunova@gmail.com<br>github.com/lana-20/candy-mapping<br>daisyladybug.com</p>
</footer>

</div>
<script>
function toggleTheme() {{
  const r = document.documentElement;
  const cur = r.getAttribute('data-theme') ||
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  r.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
}}

const bisect = {bisect_json};
const boundary = {{lo: {boundary['discard_ms']}, hi: {boundary['success_ms']}}};
const slider = document.getElementById('slider');
const msval = document.getElementById('msval');
const dot = document.getElementById('dot');
const band = document.getElementById('band');

const trackMin = 1000, trackMax = 25000;
function pct(ms) {{ return (Math.log10(ms) - Math.log10(trackMin)) / (Math.log10(trackMax) - Math.log10(trackMin)) * 100; }}
const zone = document.createElement('div');
zone.className = 'zone';
zone.style.left = pct(boundary.lo) + '%';
zone.style.width = Math.max(pct(boundary.hi) - pct(boundary.lo), 0.5) + '%';
band.appendChild(zone);

function nearestOutcome(ms) {{
  // below the measured discard point -> swallowed; at/above success point -> worked;
  // between, the real boundary sits between 3687 and 4199, so treat >= hi as worked.
  return ms >= boundary.hi ? 'worked' : 'swallowed';
}}

function update() {{
  const ms = Number(slider.value);
  msval.textContent = ms + 'ms';
  const outcome = nearestOutcome(ms);
  dot.textContent = outcome === 'worked' ? 'WORKED' : 'SWALLOWED';
  dot.className = outcome;
}}
slider.addEventListener('input', update);
update();
</script>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(ROOT)}  ({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
