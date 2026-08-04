# PNSQC 2026 poster — TODO

Resume point for what's left before this goes in. `PNSQC-PROPOSAL.md`'s own "Before
submitting — open items" checklist is fully checked off (2026-08-04) — everything below
is what's left *after* that, not a duplicate of it.

## Not yet done

- [ ] **Check the poster board against the official PNSQC template.** The sibling
      Vibium AX proposal (`~/pnsqc-2026-poster/references/PNSQC-PROPOSAL.md`, archived)
      did this — trim size, banner/logo placement, content margins, section-order
      deviation (conclusions-first vs. the template's Abstract → Intro → Approach →
      Conclusion) — and documented it as a "confirm with the committee" open point.
      Candy-mapping's `poster-board.html` was built the same way (same brand assets,
      same layout system) but was never checked against
      `PNSQC-2026-Poster-Template-Portrait.pptx` explicitly. Do that before printing.
- [ ] **Write the handout** (1–2 pages, due with the first poster draft, Sept 28). AX's
      proposal had one planned (the three-way partition as worked example, a
      how-to-reproduce section, an audit checklist, two open questions + QR code).
      Candy-mapping's equivalent: the window-drift finding as the worked example, how to
      run `probe.sh`/`attribute.sh`/`bisect.sh` yourself, and a QR to
      github.com/lana-20/candy-mapping.
- [ ] **Actually submit** — title, abstract (now 499 words), bio, optional sketch — to
      the PNSQC program committee (pnsqc.org/conference/2026/poster/). Deadline rolling,
      closes when spots fill or Sept 22, 2026.
- [ ] **Print test** — Chrome → Print → Save as PDF → A0, margins None, background
      graphics ON. Confirm the actual PDF at 841×1189mm before assuming the HTML→PDF
      pipeline holds up at full size (never done end to end yet, only screenshot-verified
      in-browser).

## Housekeeping

- [x] Committed and pushed the abstract trim, "why MCP is slower" additions across
      poster/proposal/timing-methodology/index.html/README, and the
      Vibium-verification-layer wording — 2026-08-04.
- [ ] `~/pnsqc-2026-poster` (the archived sibling) has an uncommitted `STATUS.md` archive
      note but isn't a git repo, so there's nothing to push there — just noting it's a
      local-only edit, in case that project is ever revived and initialized as a repo.

## Already done (2026-08-04), not re-litigate

- All six `PNSQC-PROPOSAL.md` open items (multi-submission policy — moot, attribution
  wording, easel cross-reference — moot, re-verified 3.7–4.2s window at n=50/50, bio sync
  — moot, cost-tracking decision).
- Sibling Vibium AX poster archived; this is the sole submission.
- Abstract trimmed from 644 to 499 words.
- "Vibium as the verification layer for coding agents" wired into proposal, poster board,
  and poster companion.
- "Why MCP is slower" (8 stacked reasoning turns vs. one fixed script) wired into the
  proposal, poster board, poster companion, `references/timing-methodology.md`,
  `index.html`, and `README.md`.
