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
# ────────────────────────────────────────────────────────────────────────────
