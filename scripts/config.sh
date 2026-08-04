#!/usr/bin/env bash
# Shared target configuration — edit this file, both scripts read it.
# ── CONFIG — edit for the target ────────────────────────────────────────────
URL="https://candymapper.com/"
DISMISS="[id\$=-close-icon]"                       # modal close; "" to skip
FILL=(                                             # 'selector :: value' — separator is ' :: '
  'input[data-aid="First Name"] :: Test'              # (never "=", selectors contain it)
  'input[data-aid="CONTACT_FORM_EMAIL"] :: test@example.invalid'
)
ACTION='button[data-aid="CONTACT_SUBMIT_BUTTON_REND"]'
SUCCESS='thank you for your inquiry'               # be SPECIFIC — see note at foot of file
COLD_CACHE=1                                       # 1 = clear cookies each run

# Extra fields — not used by probe.sh/bisect.sh (unchanged, still First Name + Email
# only). Used by journey_cli.sh/journey_mcp.sh for the fuller 8-step journey. Full map
# and how it was collected: references/selectors.md
LAST_NAME_SEL='input[data-aid="Last Name"]'         # optional field, not enforced
VALIDATION_TEXT='Please enter a valid email address' # confirmed live 2026-08-04, client-side, instant
# ────────────────────────────────────────────────────────────────────────────
