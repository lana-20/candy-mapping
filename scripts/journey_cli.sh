#!/usr/bin/env bash
# The exact canonical test case, scripted — see references/test-case.md, recorded
# verbatim from the user 2026-08-04. Do not diverge from that file without updating it
# first.
#
#   1. go  2. dismiss  3. scroll to Contact Us  4. fill first+last name
#   5. submit w/o email  6. verify validation error (bounded, non-blocking)
#   7. fill email  8. submit again (THE timed click) + verify success
#
# Logs one JSON file per run.
#
# Usage: bash journey_cli.sh [n_runs]        default 50
#
# Resumable: re-running skips any run_NN.json that already exists, same pattern as the
# sibling PNSQC harness's run_task.sh.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
source "$HERE/config.sh"

V="${VIBIUM:-vibium}"
N="${1:-50}"
OUT="$ROOT/data/runs/cli"
mkdir -p "$OUT"

for i in $(seq 1 "$N"); do
  RUN=$(printf "%02d" "$i")
  RESULT_FILE="$OUT/run_${RUN}.json"
  if [ -f "$RESULT_FILE" ]; then
    echo "[cli $RUN/$N] already exists, skipping"
    continue
  fi

  echo "[cli $RUN/$N] starting"
  TS_START=$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())')
  T0=$(python3 -c 'import time; print(time.time())')

  # Fresh browser + profile every run — no state carries between samples.
  $V stop >/dev/null 2>&1
  $V start >/dev/null 2>&1

  $V go "$URL" >/dev/null 2>&1

  if [ -n "$DISMISS" ]; then
    $V wait "$DISMISS" --state visible --timeout 10000 >/dev/null 2>&1 \
      && $V click "$DISMISS" >/dev/null 2>&1
  fi

  # Step 3 — scroll to Contact Us. The heading itself has no stable selector (see
  # selectors.md); scroll the form's own First Name field into view instead.
  $V scroll into-view 'input[data-aid="First Name"]' >/dev/null 2>&1

  # Step 4 — fill first and last name.
  $V fill 'input[data-aid="First Name"]' "Test" >/dev/null 2>&1
  $V fill "$LAST_NAME_SEL" "Testerson" >/dev/null 2>&1

  # Step 5 — submit without email. Not the timed click.
  $V click "$ACTION" >/dev/null 2>&1

  # Step 6 — verify the validation error. This click is itself subject to the SAME
  # startup race as the real submit (step 8) — confirmed live 2026-08-04: fired early
  # (~2-3s, this flow's natural timing) it's often silently swallowed, no error appears;
  # fired late (tested at 5s) it reliably shows. A long/blocking wait here would force
  # every run past the same window step 8 needs to land inside — so this check is
  # bounded (800ms) and non-fatal. A "false" reading means step 5's click was raced, not
  # that this check is broken — see references/test-case.md for the full reasoning.
  if $V wait text "$VALIDATION_TEXT" --timeout 800 >/dev/null 2>&1; then
    VALIDATED=true
  else
    VALIDATED=false
  fi

  # Step 7 — fill email.
  $V fill 'input[data-aid="CONTACT_FORM_EMAIL"]' "test@example.invalid" >/dev/null 2>&1
  got=$($V value 'input[data-aid="CONTACT_FORM_EMAIL"]' 2>/dev/null)
  if [ "$got" != "test@example.invalid" ]; then
    echo "  PRECONDITION FAILED — email field holds [$got]"
    python3 - "$RESULT_FILE" "$i" "$TS_START" "$VALIDATED" <<'PY'
import json, sys
json.dump({"run": int(sys.argv[2]), "ts_start": sys.argv[3], "arrival_ms": None,
           "wall_ms": None, "result": "precondition_failed",
           "validation_confirmed": sys.argv[4] == "true"}, open(sys.argv[1], "w"), indent=2)
PY
    continue
  fi

  # Arm the detector BEFORE the timed click — same technique as probe.sh.
  $V eval 'window.__hit="";window.__before=document.body.innerText;
    new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes){
    const s=(n.innerText||n.textContent||"");if(new RegExp("'"$SUCCESS"'","i").test(s)&&s.length<400)
    window.__hit=s.trim()}}).observe(document.body,{childList:true,subtree:true});"armed"' >/dev/null 2>&1

  # Step 8 — submit again. THE timed click. Timestamp + click in one eval call
  # (probe.sh's fix): no inter-process gap between "the time we recorded" and "the click
  # that fired". Success text checked against is config.sh's SUCCESS pattern, a safe
  # substring of the full published text ("Thank you for your inquiry! We will get back
  # to you within 48 Years.").
  AGE=$($V eval "(()=>{const t=Math.round(performance.now());document.querySelector('${ACTION}').click();return t})()" 2>/dev/null)
  $V sleep 3000 >/dev/null 2>&1

  RESULT=$($V eval '(()=>{const re=new RegExp("'"$SUCCESS"'","i");
    const appeared = re.test(document.body.innerText) && !re.test(window.__before||"");
    return (window.__hit || appeared) ? "worked" : "SWALLOWED"})()' 2>/dev/null)

  T1=$(python3 -c 'import time; print(time.time())')
  WALL_MS=$(python3 -c "print(round((${T1}-${T0})*1000))")

  # Log the literal string, not a boolean — "hit: true/false" is ambiguous (hit the
  # bug? hit the success path?) and produced exactly that confusion once already this
  # session. "result": "worked"/"SWALLOWED" reads the same way in the JSON as it does
  # in every printed log line and every published table — no inversion to remember.
  python3 - "$RESULT_FILE" "$i" "$TS_START" "$AGE" "$RESULT" "$WALL_MS" "$VALIDATED" <<'PY'
import json, sys
run, ts_start, age, result, wall, validated = sys.argv[2:8]
json.dump({
    "run": int(run), "ts_start": ts_start,
    "arrival_ms": int(age) if age.strip().isdigit() else None,
    "wall_ms": int(wall), "result": result,
    "validation_confirmed": validated == "true",
}, open(sys.argv[1], "w"), indent=2)
PY

  printf '[cli %s/%s] t+%sms -> %s (wall %sms, validation_confirmed=%s)\n' "$RUN" "$N" "$AGE" "$RESULT" "$WALL_MS" "$VALIDATED"
  $V stop >/dev/null 2>&1
  sleep 2   # pace real submissions to the live site
done

$V daemon stop >/dev/null 2>&1
echo "done -> $OUT"
