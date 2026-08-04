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
- [x] **Write the handout** (1–2 pages, due with the first poster draft, Sept 28) —
      `scripts/build_handout.py` → `assets/handout.html`, 2 US Letter pages. Page 1: the
      window-drift finding as the worked example (original 10-probe timeline SVG +
      3-bisection creep table). Page 2: `probe.sh`/`attribute.sh`/`bisect.sh` walkthrough,
      a 5-item "how to catch an overstated finding" checklist (this project's own real
      mistakes — the drift overstatement, the `bisect.sh` exit-code bug, the FATAL-regex
      false-negative/positive, quarantine-not-delete), two open questions for the
      reviewer, and a QR code (`assets/qr-repo.svg`, pre-generated with the `qrcode`
      python package, not a build-time dependency) to github.com/lana-20/candy-mapping.
      Screenshot-verified 2026-08-04.
- [ ] **Actually submit** — title, abstract (now 499 words), bio, optional sketch,
      handout — to the PNSQC program committee (pnsqc.org/conference/2026/poster/).
      Deadline rolling, closes when spots fill or Sept 22, 2026.
- [ ] **Print test — genuinely not done, and `vibium pdf` cannot do it.** Tried
      `vibium pdf` against both `poster-board.html` (should be 841×1189mm/A0) and
      `handout.html` (should be 2× Letter) — **it ignores the page's own `@page` CSS
      entirely and always emits Letter (612×792pt) regardless of what's declared.** The
      handout "passed" only by coincidence (its `@page` already says `letter`); the board
      test proves the tool can't validate A0 at all. Real verification requires manual
      Chrome: File → Print → Save as PDF → pick the paper size by hand (A0 for the board,
      Letter for the handout) → margins None → background graphics ON, then check the
      resulting PDF's actual page size. Not yet done for either file.

## Housekeeping

- [x] Committed and pushed the abstract trim, "why MCP is slower" additions across
      poster/proposal/timing-methodology/index.html/README, and the
      Vibium-verification-layer wording — 2026-08-04.
- [ ] `~/pnsqc-2026-poster` (the archived sibling) has an uncommitted `STATUS.md` archive
      note but isn't a git repo, so there's nothing to push there — just noting it's a
      local-only edit, in case that project is ever revived and initialized as a repo.

## Already done (2026-08-04), not re-litigate

- All six `PNSQC-PROPOSAL.md` open items (multi-submission policy — moot, attribution
  wording, easel cross-reference — moot, re-verified 3.7–4.2s window at n=70/70, bio sync
  — moot, cost-tracking decision).
- Sibling Vibium AX poster archived; this is the sole submission.
- Abstract trimmed from 644 to 499 words.
- "Vibium as the verification layer for coding agents" wired into proposal, poster board,
  and poster companion.
- "Why MCP is slower" (8 stacked reasoning turns vs. one fixed script) wired into the
  proposal, poster board, poster companion, `references/timing-methodology.md`,
  `index.html`, and `README.md`.
- The 2-page handout (see above) — content and layout done; the print-size *test* is not
  (see the open item above, `vibium pdf` can't validate it, needs manual Chrome).
- **Hardening extended 50/50 → 70/70 the same day** (resumable harness just picked up at
  run 51 for each arm) — 69/70 CLI, 70/70 MCP, arrival medians 4,710ms/21,986ms, ratio
  ~4.7× (was ~4.6× at n=50). Propagated everywhere the n=50 figures were published: both
  poster artifacts, the handout, `PNSQC-PROPOSAL.md` (title alternates too), `README.md`,
  `index.html`, `references/{timing-methodology,methodology,test-case}.md`,
  `vibium-mcp-flow.html`, `vibium-test-case-commands.html`. Also caught and fixed a
  leftover overstated drift claim ("moved by roughly two seconds") in
  `PNSQC-PROPOSAL.md`'s Framing section that survived the earlier correction pass.
