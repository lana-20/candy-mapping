"""
Shared SVG chart builders for build_board.py and build_poster.py.

Ports the two hand-designed charts from index.html (the published article) so the
poster reuses the same visual language instead of inventing a new one: the zoned
boundary timeline, and the build-time-vs-run-time quadrant grid with Paul Grossman's
16 tools plus Vibium's two entries. Colors are CSS custom properties (var(--x)) so
the same markup works in both the fixed-palette print board and the light/dark web
companion — this is inlined into live HTML, not rasterized, so the browser resolves
them per-page.
"""


def timeline_svg(bisect, boundary, w=1200, h=440):
    """Zoned boundary timeline: discard zone, hatched uncertainty strip, success
    zone, boundary callout, one dot per measured probe. Linear scale over the full
    observed range so every probe is on-scale (the article's version capped at 8s
    and called out two points as off-scale; here nothing is). The dot strip sits
    in its own band below the zone text so stacked/clustered probes never overlap
    the "SUBMIT DISCARDED/WORKS" labels — h must be >= 440 (default) to fit it."""
    m_l, m_r = 70, 70
    zone_top, zone_h = 60, 150
    zone_bottom = zone_top + zone_h
    dot_strip_top = zone_bottom + 24
    dot_strip_h = 110
    axis_y = dot_strip_top + dot_strip_h

    lo_ms = boundary["discard_ms"]
    hi_ms = boundary["success_ms"]
    max_ms = max(p["ms"] for p in bisect) * 1.08

    def x(ms):
        return m_l + (ms / max_ms) * (w - m_l - m_r)

    lo_x, hi_x = x(lo_ms), x(hi_ms)

    fill_h = axis_y - zone_top
    zones = (
        f'<rect x="{m_l}" y="{zone_top}" width="{lo_x-m_l:.1f}" height="{fill_h}" fill="var(--bad)" opacity="0.13"/>'
        f'<rect x="{lo_x:.1f}" y="{zone_top}" width="{hi_x-lo_x:.1f}" height="{fill_h}" fill="var(--rule2)" opacity="0.35"/>'
        f'<rect x="{hi_x:.1f}" y="{zone_top}" width="{w-m_r-hi_x:.1f}" height="{fill_h}" fill="var(--cli)" opacity="0.13"/>'
        f'<rect x="{m_l}" y="{zone_top}" width="{w-m_l-m_r:.1f}" height="{fill_h}" fill="none" stroke="var(--rule)"/>'
        f'<line x1="{lo_x:.1f}" y1="{zone_top}" x2="{lo_x:.1f}" y2="{axis_y}" stroke="var(--bad)" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>'
        f'<line x1="{hi_x:.1f}" y1="{zone_top}" x2="{hi_x:.1f}" y2="{axis_y}" stroke="var(--cli)" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>'
    )
    zone_mid_lo = (m_l + lo_x) / 2
    zone_mid_hi = (hi_x + w - m_r) / 2
    labels = (
        f'<text x="{zone_mid_lo:.1f}" y="{zone_top+zone_h/2-8:.1f}" text-anchor="middle" font-family="var(--sans)" '
        f'font-size="26" font-weight="700" fill="var(--bad)" letter-spacing="-0.5">SUBMIT DISCARDED</text>'
        f'<text x="{zone_mid_lo:.1f}" y="{zone_top+zone_h/2+18:.1f}" text-anchor="middle" font-family="var(--sans)" '
        f'font-size="13" fill="var(--ink3)">the page takes the click and does nothing</text>'
        f'<text x="{zone_mid_hi:.1f}" y="{zone_top+zone_h/2-8:.1f}" text-anchor="middle" font-family="var(--sans)" '
        f'font-size="26" font-weight="700" fill="var(--cli)" letter-spacing="-0.5">SUBMIT WORKS</text>'
        f'<text x="{zone_mid_hi:.1f}" y="{zone_top+zone_h/2+18:.1f}" text-anchor="middle" font-family="var(--sans)" '
        f'font-size="13" fill="var(--ink3)">every time, exactly as designed</text>'
    )
    callout_cx = (lo_x + hi_x) / 2
    callout = (
        f'<rect x="{callout_cx-58:.1f}" y="{zone_top-40}" width="116" height="26" rx="13" fill="var(--ink)"/>'
        f'<text x="{callout_cx:.1f}" y="{zone_top-22}" text-anchor="middle" font-family="var(--mono)" '
        f'font-size="13" font-weight="600" fill="var(--ground)">{boundary["window_lo"]}–{boundary["window_hi"]}s</text>'
        f'<line x1="{callout_cx:.1f}" y1="{zone_top-14}" x2="{callout_cx:.1f}" y2="{zone_top}" stroke="var(--ink)" stroke-width="2"/>'
    )

    ticks = []
    step = 4000 if max_ms > 15000 else 2000
    t = 0
    while t <= max_ms:
        tx = x(t)
        ticks.append(
            f'<line x1="{tx:.1f}" y1="{axis_y-4}" x2="{tx:.1f}" y2="{axis_y+4}" stroke="var(--rule2)" stroke-width="1.5"/>'
            f'<text x="{tx:.1f}" y="{axis_y+20}" text-anchor="middle" font-family="var(--mono)" font-size="12" fill="var(--ink3)">{t/1000:g}s</text>'
        )
        t += step
    axis = f'<line x1="{m_l}" y1="{axis_y}" x2="{w-m_r}" y2="{axis_y}" stroke="var(--rule)" stroke-width="2"/>' + "".join(ticks)

    # declutter: points landing within min_gap px of the previous one stack onto a
    # higher tier (no per-dot numeric labels, matching the original article chart —
    # exact ms values are stated in prose instead, so overlapping text is never a
    # risk here, only overlapping circles).
    ordered = sorted(bisect, key=lambda p: p["ms"])
    min_gap = 16
    tiers, last_x = [], None
    for p in ordered:
        cx = x(p["ms"])
        tier = 0 if last_x is None or cx - last_x >= min_gap else tiers[-1] + 1
        tiers.append(tier)
        last_x = cx
    tier_of = {p["ms"]: t for p, t in zip(ordered, tiers)}

    dots = ""
    for p in bisect:
        cx = x(p["ms"])
        dot_y = axis_y - 16 - tier_of[p["ms"]] * 15
        ok = p["result"] == "worked"
        color = "var(--cli)" if ok else "var(--bad)"
        dots += f'<circle cx="{cx:.1f}" cy="{dot_y:.1f}" r="6.5" fill="{color}" stroke="var(--panel)" stroke-width="1.5"/>'

    caption = (
        f'<text x="{m_l}" y="{axis_y+56}" font-family="var(--sans)" font-size="13" font-weight="600" '
        f'fill="var(--ink2)">Time of click, measured from page load</text>'
        f'<text x="{w-m_r}" y="{axis_y+56}" text-anchor="end" font-family="var(--sans)" font-size="12" '
        f'fill="var(--ink3)">each dot is one real submission attempt</text>'
    )

    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" height="auto" role="img" '
        f'aria-label="Timeline of ten measured Submit clicks. Clicks before {boundary["window_lo"]}s are '
        f'discarded by the page; clicks after {boundary["window_hi"]}s succeed.">'
        f'{zones}{labels}{callout}{axis}{dots}{caption}</svg>'
    )


def grid_svg(grid, w=860, h=470):
    """Build-time-vs-run-time quadrant scatter: Paul Grossman's 16 published tools
    (neutral dots) plus Vibium's CLI and MCP entries highlighted, with the MCP
    entry's build-time bar (build cost moved into every run) shown as a range."""
    m_l, m_r, m_t, m_b = 60, 24, 24, 56
    pw, ph = w - m_l - m_r, h - m_t - m_b
    x0, x1 = 132, 0
    y0, y1 = -0.6, 25.6
    xd, yd = 65, 12.5

    def sx(s):
        return m_l + (x0 - s) / (x0 - x1) * pw

    def sy(mm):
        return m_t + (mm - y0) / (y1 - y0) * ph

    quads = [
        (m_l, m_t, sx(xd) - m_l, sy(yd) - m_t, "var(--rule2)", 0.10),
        (sx(xd), m_t, m_l + pw - sx(xd), sy(yd) - m_t, "var(--cli)", 0.08),
        (m_l, sy(yd), sx(xd) - m_l, m_t + ph - sy(yd), "var(--bad)", 0.08),
        (sx(xd), sy(yd), m_l + pw - sx(xd), m_t + ph - sy(yd), "var(--mcp)", 0.08),
    ]
    parts = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{hh:.1f}" fill="{c}" opacity="{o}"/>'
             for x, y, ww, hh, c, o in quads]
    parts.append(f'<line x1="{sx(xd):.1f}" y1="{m_t}" x2="{sx(xd):.1f}" y2="{m_t+ph}" stroke="var(--rule2)" stroke-dasharray="5 4"/>')
    parts.append(f'<line x1="{m_l}" y1="{sy(yd):.1f}" x2="{m_l+pw}" y2="{sy(yd):.1f}" stroke="var(--rule2)" stroke-dasharray="5 4"/>')
    parts.append(f'<rect x="{m_l}" y="{m_t}" width="{pw}" height="{ph}" fill="none" stroke="var(--rule)"/>')

    quad_labels = [
        ("Quick Starters", m_l + 10, m_t + 18, "start"),
        ("Speedsters", m_l + pw - 10, m_t + 18, "end"),
        ("Room to Grow", m_l + 10, sy(yd) + 22, "start"),
        ("Steady Performers", m_l + pw - 10, sy(yd) + 22, "end"),
    ]
    for t, x, y, a in quad_labels:
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{a}" font-family="var(--sans)" '
                     f'font-size="11" font-weight="700" fill="var(--ink3)">{t}</text>')

    for t in (125, 100, 75, 50, 25, 1):
        parts.append(f'<text x="{sx(t):.1f}" y="{m_t+ph+18}" text-anchor="middle" font-family="var(--mono)" '
                     f'font-size="9.5" fill="var(--ink3)">{t}s</text>')
    for t in (1, 5, 10, 15, 20, 25):
        parts.append(f'<text x="{m_l-8}" y="{sy(t)+3:.1f}" text-anchor="end" font-family="var(--mono)" '
                     f'font-size="9.5" fill="var(--ink3)">{t}m</text>')
    parts.append(f'<text x="{m_l}" y="{h-8}" font-family="var(--sans)" font-size="10.5" font-weight="600" '
                 f'fill="var(--ink2)">Run time — less is better →</text>')
    parts.append(f'<text transform="translate(14 {m_t+ph}) rotate(-90)" font-family="var(--sans)" '
                 f'font-size="10.5" font-weight="600" fill="var(--ink2)">Build time — less is better →</text>')

    def fmt_b(v):
        return "0m" if v < 1 else (f"{int(v)}m" if float(v).is_integer() else f"{v:.2f}".rstrip("0") + "m")

    for d in grid["tools"]:
        x, y = sx(d["r"]), sy(d["b"])
        dy, ax, dx = d.get("dy", 15), d.get("ax", "middle"), d.get("dx", 0)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="var(--ink3)"/>')
        parts.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{ax}" font-family="var(--sans)" '
                     f'font-size="9" fill="var(--ink3)">{d["n"]}</text>')

    for d in grid["mine"]:
        x, y = sx(d["r"]), sy(d["b"])
        xlo, xhi = sx(d["lo"]), sx(d["hi"])
        color = f'var(--{d["series"]})'
        dy, ax, dx = d.get("dy", -13), d.get("ax", "middle"), d.get("dx", 0)
        parts.append(f'<line x1="{xlo:.1f}" y1="{y:.1f}" x2="{xhi:.1f}" y2="{y:.1f}" stroke="{color}" '
                     f'stroke-width="2.5" opacity="0.5" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{color}" opacity="0.18"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{color}" stroke="var(--panel)" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{ax}" font-family="var(--sans)" '
                     f'font-size="11.5" font-weight="700" fill="{color}">{d["n"]}</text>')
        parts.append(f'<text x="{x+dx:.1f}" y="{y+dy+12:.1f}" text-anchor="{ax}" font-family="var(--mono)" '
                     f'font-size="9.5" fill="{color}" opacity="0.9">{d["sub"]}</text>')

    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" height="auto" role="img" '
        f'aria-label="Build time versus run time for sixteen published tools plus Vibium CLI and MCP on the '
        f'CandyMapper challenge.">' + "".join(parts) + '</svg>'
    )
