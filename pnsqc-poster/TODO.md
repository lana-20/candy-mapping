# PNSQC 2026 poster — TODO

Resume point for what's left before this goes in. `PNSQC-PROPOSAL.md`'s own "Before
submitting — open items" checklist is fully checked off (2026-08-04) — everything below
is what's left *after* that, not a duplicate of it.

## Poster optimization plan (2026-08-05) — priority order, with time estimates

Prompted by adding a "robustness check" paragraph to `PNSQC-PROPOSAL.md` citing
`vibium-efficiency`'s hardened n=50 batched-MCP result (~17.3s median, still ~4× outside
the window). That addition is proposal-text only so far — nothing below assumes it's
decided to go on the printed board; item 1 is that decision itself.

1. **Decide + (if yes) implement the robustness-check addition on the printed
   artifacts** — ~20 min to decide, ~30–40 min to implement if yes.
   - Decide: does "even optimized MCP misses by ~4×" earn poster-board space, or stay
     proposal-only as reviewer/easel backup? Leans toward **footnote-only, not a new
     poster panel** — the poster's own positioning rules (one clean two-minute repro, no
     extra angles) argue against a second dataset competing for attention with the
     headline 69/70 vs 70/70 split. A single small caption under the MCP arrival stat
     ("batched: ~17.3s, n=50 — still outside") is the max scope worth considering.
   - If yes: add a `"mcp_optimized"` key to `assets/poster_data.json` (n=50, median
     17,254ms, mean 18,007ms, stdev 2,920ms — pulled from
     `~/vibium-efficiency/data/runs/mcp_batched/`) and wire a small caption/footnote into
     `poster-board.html` and `poster.html` near the existing MCP arrival stat. Re-run
     `scripts/build_handout.py`-equivalent regeneration if the board is templated from
     the JSON (check how `poster-board.html` currently consumes `poster_data.json` before
     assuming a rebuild step exists).
   - If no: cross this off, leave the proposal paragraph as-is (already done), done.
2. **Check the poster board against the official PNSQC template** — ~30–45 min.
   (Carried over from below — resequenced to before the print test, since a template
   mismatch found here could change margins/layout the print test would otherwise have
   to redo.) Trim size, banner/logo placement, content margins, section-order deviation
   (this poster is conclusions-first vs. the template's Abstract → Intro → Approach →
   Conclusion) against `~/Desktop/PNSQC-2026-Poster-Template-Landscape.pptx` /
   `-Portrait.pptx`. The sibling archived Vibium AX proposal already did this once — reuse
   its checklist/approach if still findable in `~/pnsqc-2026-poster/references/PNSQC-PROPOSAL.md`
   rather than re-deriving from scratch.
3. **Print test — manual Chrome, not `vibium pdf`** — ~15–20 min. `vibium pdf` is
   confirmed unusable for this (ignores `@page` CSS, always emits Letter — see
   `feedback_vibium_pdf_page_size.md` in memory). File → Print → Save as PDF → pick A0 by
   hand for `poster-board.html`, Letter for `handout.html` → margins None → background
   graphics ON → verify the resulting PDF's actual page size. Do this *after* item 2, in
   case the template check changes the board's dimensions.
4. **Actually submit** — ~15 min of form-filling, assuming items 1–3 are settled and
   nothing they surface requires more poster-content changes. Title, abstract (499
   words), bio, optional sketch, handout, submitted at
   pnsqc.org/conference/2026/poster/. Deadline rolling, closes when spots fill or
   Sept 22, 2026 — no reason to rush ahead of items 1–3, since a template mismatch or a
   late decision to add the robustness caption is far cheaper to fix before submission
   than after.

**Total: ~2–2.5 hours** across all four, dominated by item 2 (template check) and the
implementation half of item 1 if that's the decision — items 3 and 4 are quick once the
content is settled.

## Already done, folded out of the active sequence above

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

(The template check, print test, and submission steps are now items 2–4 in the
sequenced plan above — not repeated here to avoid two copies drifting out of sync.)

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
