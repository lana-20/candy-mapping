#!/usr/bin/env python3
"""
Build the print-ready poster handout: assets/handout.html

  python3 scripts/build_handout.py

Two US Letter pages (8.5 x 11 in), matching the "1-2 page handout, due with the
first poster draft" PNSQC deliverable. Self-contained (data + QR inlined) —
open in Chrome, Print, "Save as PDF", paper Letter, margins Default,
background graphics ON.

The QR SVG at assets/qr-repo.svg was pre-generated once via the `qrcode`
package (not a runtime dependency of this script — see git history for the
one-off command) and is just read as a static asset here, same as
brand()/photo() in build_board.py.
"""

import json
from pathlib import Path

from chart_lib import timeline_svg

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "handout.html"


def qr():
    p = ROOT / "assets" / "qr-repo.svg"
    if not p.exists():
        raise SystemExit(f"missing {p.relative_to(ROOT)} — nothing to build from")
    return p.read_text()


def main():
    data_path = ROOT / "assets" / "poster_data.json"
    if not data_path.exists():
        raise SystemExit(f"missing {data_path.relative_to(ROOT)} — nothing to build from")
    data = json.loads(data_path.read_text())
    b = data["boundary"]
    hard = data["hardening"]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Handout — Quality in the Age of Autonomy — PNSQC 2026</title>
<style>
@page {{ size: letter; margin: 0.55in; }}
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
  background:var(--ground); color:var(--ink); font-family:var(--sans);
  font-size:10.5px; line-height:1.42; -webkit-print-color-adjust:exact; print-color-adjust:exact;
}}
.page {{ width:7.4in; margin:0 auto; padding:6px 0 0; page-break-after:always; }}
.page:last-child {{ page-break-after:auto; }}

h1 {{ font-size:26px; line-height:1.04; letter-spacing:-0.02em; font-weight:800; margin:4px 0 6px; }}
h2 {{ font-size:15px; line-height:1.15; letter-spacing:-0.01em; font-weight:750; margin:0 0 6px; }}
h3 {{ font-size:12.5px; font-weight:700; margin:0 0 4px; }}
p  {{ margin:0 0 8px; }}
.kick {{ font-family:var(--mono); font-size:9px; letter-spacing:0.16em; text-transform:uppercase;
        color:var(--cli); font-weight:700; }}
.eyebrow {{ font-family:var(--mono); font-size:9px; letter-spacing:0.13em; text-transform:uppercase;
           color:var(--ink3); font-weight:600; margin-bottom:5px; }}
.small {{ font-size:10.5px; color:var(--ink3); line-height:1.4; }}

header {{ border-bottom:1.6px solid var(--ink); padding-bottom:8px; margin-bottom:12px; }}
.byline {{ display:flex; flex-wrap:wrap; gap:2px 16px; margin-top:6px;
          font-family:var(--mono); font-size:9.5px; color:var(--ink3); }}
.byline b {{ color:var(--ink2); }}

.figrow {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--rule);
          border:1px solid var(--rule); margin-bottom:14px; }}
.fig {{ background:var(--ground); padding:8px 9px 9px; }}
.figv {{ font-family:var(--mono); font-variant-numeric:tabular-nums; font-size:19px;
        font-weight:700; line-height:1; letter-spacing:-0.02em; }}
.figv.a {{ color:var(--cli); }} .figv.b {{ color:var(--bad); }}
.figl {{ font-size:9px; color:var(--ink3); margin-top:4px; line-height:1.3; }}

.tlwrap {{ background:var(--sunk); border-radius:2px; padding:8px; margin-bottom:14px; }}

table {{ border-collapse:collapse; width:100%; font-size:10px; margin-bottom:14px; }}
th,td {{ padding:4px 7px; text-align:left; border-bottom:0.8px solid var(--rule); }}
thead th {{ font-family:var(--mono); font-size:8.5px; letter-spacing:0.06em; text-transform:uppercase;
           color:var(--ink3); background:var(--sunk); }}
td.n, th.n {{ text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums; }}
tbody tr:last-child td {{ border-bottom:0; }}

.steps {{ counter-reset:s; margin-bottom:14px; }}
.step {{ display:grid; grid-template-columns:18px 1fr; gap:8px; margin-bottom:9px; }}
.step::before {{ counter-increment:s; content:counter(s); font-family:var(--mono); font-size:9.5px;
                font-weight:700; color:var(--cli); border:1px solid var(--rule2); border-radius:50%;
                width:18px; height:18px; display:grid; place-items:center; }}
.step b {{ font-size:11px; }} .step p {{ font-size:10px; color:var(--ink3); line-height:1.35; margin:2px 0 0; }}
pre {{ font-family:var(--mono); font-size:9.3px; background:var(--sunk); padding:7px 8px;
      border-radius:2px; overflow:hidden; white-space:pre-wrap; line-height:1.5; color:var(--ink2);
      margin:0 0 14px; }}
code {{ font-family:var(--mono); font-size:0.92em; }}

.panel {{ background:var(--panel); border:1px solid var(--rule); padding:9px 10px 10px; margin-bottom:14px; }}
.panel.sunk {{ background:var(--sunk); }}
.checklist {{ margin:0; padding-left:0; list-style:none; }}
.checklist li {{ font-size:10.3px; color:var(--ink2); line-height:1.38; margin-bottom:7px;
                padding-left:20px; position:relative; }}
.checklist li::before {{ content:"\\2610"; position:absolute; left:0; color:var(--ink3); font-size:11px; }}
.checklist b {{ color:var(--ink); }}

.qgrid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-bottom:14px; }}
.q {{ background:var(--sunk); border-left:3px solid var(--cli); padding:8px 10px; }}
.q b {{ display:block; font-size:10.3px; margin-bottom:3px; }}
.q p {{ font-size:9.8px; color:var(--ink3); margin:0; line-height:1.35; }}

footer {{ display:grid; grid-template-columns:1fr auto; gap:16px; align-items:center;
         border-top:1.4px solid var(--ink); padding-top:10px; }}
footer .links {{ font-size:9.8px; color:var(--ink3); line-height:1.55; }}
footer .links b {{ color:var(--ink); }}
footer .qr {{ width:0.85in; height:0.85in; }}
footer .qr svg {{ width:100%; height:100%; display:block; }}
footer .qrwrap {{ display:flex; flex-direction:column; align-items:center; gap:3px; }}
footer .qrwrap span {{ font-family:var(--mono); font-size:7.5px; color:var(--ink3); }}

.pagefoot {{ text-align:center; font-family:var(--mono); font-size:8px; color:var(--rule2);
            margin-top:10px; }}
</style></head>
<body>

<div class="page">
  <header>
    <p class="kick">PNSQC 2026 &middot; Poster Handout &middot; 1 of 2</p>
    <h1>Quality in the age of autonomy: deliberation costs you the bug.</h1>
    <div class="byline">
      <span><b>Lana Begunova</b> &middot; Daisy Lady Bug &middot; begunova@gmail.com</span>
      <span>AUT <b>candymapper.com</b></span>
      <span>Tool <b>Vibium v26.5.31</b> &middot; CLI + MCP</span>
    </div>
  </header>

  <p class="small">CandyMapper.com's contact form has a Submit button that's clickable before its own
    handler finishes wiring up. The first click after page load is silently discarded &mdash; no error,
    no request, nothing to notice. Click again and it works. Below is the worked example: how the
    window was measured, and how it turned out not to be a fixed constant.</p>

  <div class="figrow">
    <div class="fig"><div class="figv a">{b['window_lo']}&ndash;4.4s</div><div class="figl">vulnerability window, moves
      within a session</div></div>
    <div class="fig"><div class="figv b">{hard['cli']['swallowed']}/{hard['cli']['n']} &middot; {hard['mcp']['worked']}/{hard['mcp']['n']}</div><div class="figl">hardened hit rate,
      full 8-step journey, n=50 each</div></div>
    <div class="fig"><div class="figv">4.6&times;</div><div class="figl">slower arrival at Submit &mdash;
      21.3s (MCP) vs 4.7s (CLI) medians</div></div>
  </div>

  <p class="eyebrow">Worked example &mdash; the original ten-probe sweep</p>
  <div class="tlwrap">{timeline_svg(data['bisect'], b, w=1150, h=340)}</div>

  <p class="eyebrow">Then it moved &mdash; three real bisections, same session</p>
  <table>
    <thead><tr><th>When</th><th>Discard &rarr; success</th><th class="n">Creep from previous</th></tr></thead>
    <tbody>
      <tr><td>First measurement, {data['date']}</td><td class="n">3,687 &rarr; 4,199ms</td><td class="n">&mdash;</td></tr>
      <tr><td>Re-bisected ~45 min later, 2026-08-04</td><td class="n">3,941 &rarr; 4,252ms</td><td class="n">~200&ndash;250ms</td></tr>
      <tr><td>Re-bisected ~90 min later, 2026-08-04</td><td class="n">4,095 &rarr; 4,393ms</td><td class="n">~150&ndash;250ms</td></tr>
    </tbody>
  </table>
  <p class="small">Each row is a real bisection (a full sweep, not one click) &mdash; see the checklist
    on page 2 for why that distinction is the whole finding. The boundary drifts <b>within a single
    session</b>, not only session to session, by a modest and repeatable amount. Treat any published
    bracket as a snapshot of the moment it was measured, not a constant to check new data against
    later.</p>

  <p class="pagefoot">candy-mapping &middot; page 1 of 2</p>
</div>

<div class="page">
  <header>
    <p class="kick">PNSQC 2026 &middot; Poster Handout &middot; 2 of 2</p>
    <h2 style="font-size:18px">Run it yourself, and how to catch a claim like this one being wrong</h2>
  </header>

  <p class="eyebrow">Run it yourself</p>
  <div class="steps">
    <div class="step"><div><b>probe</b><p>One timed attempt at a chosen delay after load &rarr; SWALLOWED or worked.
      <code>bash scripts/probe.sh 4000</code></p></div></div>
    <div class="step"><div><b>attribute</b><p>Capture-phase listener + network hook proves the page received the
      click and discarded it &mdash; not a missed selector. <code>bash scripts/attribute.sh</code></p></div></div>
    <div class="step"><div><b>bisect</b><p>Sweeps the delay and narrows to the failure boundary automatically.
      <code>bash scripts/bisect.sh</code></p></div></div>
  </div>
  <pre>after click 1 &rarr; listener=1  xhr=[]                        message=false
after click 2 &rarr; listener=2  xhr=["POST .../v3/messages"]  message=true

The page received the first click &mdash; the counter incremented &mdash; and did nothing with it.</pre>

  <p class="eyebrow">How to catch an overstated drift claim (the mistake this project made, and fixed)</p>
  <div class="panel sunk">
    <ul class="checklist">
      <li><b>A single click is not a re-confirmation.</b> The first version of this finding claimed the
        window had moved to "6,054ms, nearly two seconds later" &mdash; based on one control click, not a
        real bisection. It was wrong. Re-bisecting properly (multiple probes) found a real but far more
        modest 150&ndash;250ms creep instead.</li>
      <li><b>Distinguish a precondition failure from a real result.</b> A bug in <code>bisect.sh</code>'s
        coarse sweep let a <code>PRECONDITION FAILED</code> (bad fill, wrong state) read identically to a
        genuine <code>SWALLOWED</code>, silently corrupting the bracket. Check the exit code explicitly,
        not a bare truthy <code>if</code>.</li>
      <li><b>Check whether local load explains a timing change before trusting the finding.</b> Verified the
        harness's own arrival times were flat/declining across the run sequence, not rising, before
        concluding the drift was real and not measurement noise.</li>
      <li><b>A rate-limit rejection can look like silence, not an error.</b> <code>claude -p</code> reports a
        session-limit rejection as a structured <em>stdout</em> JSON event, not stderr &mdash; a harness that
        only scans stderr will burn calls on instant, zero-cost failures without noticing.</li>
      <li><b>Quarantine bad batches, don't delete them.</b> Every rejected or superseded run in this
        project lives under <code>data/runs/_rejected/&lt;reason&gt;/</code> &mdash; they're the test
        fixtures for the next harness bug, not just noise to clear away.</li>
    </ul>
  </div>

  <p class="eyebrow">Two open questions for the reviewer</p>
  <div class="qgrid">
    <div class="q"><b>Does a 150&ndash;250ms boundary creep matter operationally?</b>
      <p>It's real and repeatable, but far inside the noise budget most CI gates already tolerate. Is
        "the window moves" itself the finding worth a poster, or only the underlying race?</p></div>
    <div class="q"><b>Is conclusions-first the right layout for this venue?</b>
      <p>The board leads with conclusions immediately below the masthead (Erren &amp; Bourne rule 8)
        rather than the template's Abstract &rarr; Introduction &rarr; Approach &rarr; Conclusion order.
        Branding is reproduced faithfully; the section order is not. Acceptable before printing?</p></div>
  </div>

  <footer>
    <div class="links">
      <b>Full write-up, raw data, and all scripts:</b><br>
      github.com/lana-20/candy-mapping &middot; lana-20.github.io/candy-mapping<br>
      <b>Lana Begunova</b> &middot; begunova@gmail.com &middot; daisyladybug.com
    </div>
    <div class="qrwrap">
      <div class="qr">{qr()}</div>
      <span>scan for the repo</span>
    </div>
  </footer>
  <p class="pagefoot">candy-mapping &middot; page 2 of 2</p>
</div>

</body></html>"""

    OUT.write_text(html)
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(ROOT)}  ({kb:.0f} KB) — 2 pages, US Letter")
    print('  print: Chrome -> Print -> Save as PDF -> paper Letter, margins Default, background graphics ON')


if __name__ == "__main__":
    main()
