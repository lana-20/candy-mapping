#!/usr/bin/env bash
# One probe: perform the action DELAY_MS after page load, report whether it landed.
# Usage: bash probe.sh [delay_ms]        e.g. bash probe.sh 0
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"

V="${VIBIUM:-vibium}"
DELAY_MS="${1:-0}"

[ "$COLD_CACHE" = "1" ] && $V cookies clear >/dev/null
$V go "$URL" >/dev/null

if [ -n "$DISMISS" ]; then
  $V wait "$DISMISS" --state visible --timeout 10000 >/dev/null 2>&1 \
    && $V click "$DISMISS" >/dev/null 2>&1
fi

# Fill, then READ BACK. A malformed selector can be accepted by the driver and quietly write to
# the wrong element; an unverified fill turns a failed precondition into a fake timing result.
for pair in "${FILL[@]}"; do
  sel="${pair%% :: *}"; val="${pair##* :: }"
  $V fill "$sel" "$val" >/dev/null 2>&1
  got=$($V value "$sel" 2>/dev/null)
  if [ "$got" != "$val" ]; then
    echo "PRECONDITION FAILED — '$sel' holds [$got], expected [$val]."
    echo "Fix the locator before probing; a half-filled form fails validation and looks like a race."
    exit 2
  fi
done

# Arm the detector BEFORE acting: an observer for transient confirmations, plus a snapshot of the
# page as it stands. Success must be text that appeared AFTER the click — a plain page-wide match
# will happily hit unrelated static copy and report a discarded action as a success.
$V eval 'window.__hit="";window.__before=document.body.innerText;
  new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes){
  const s=(n.innerText||n.textContent||"");if(new RegExp("'"$SUCCESS"'","i").test(s)&&s.length<400)
  window.__hit=s.trim()}}).observe(document.body,{childList:true,subtree:true});"armed"' >/dev/null

[ "$DELAY_MS" -gt 0 ] && $V sleep "$DELAY_MS" >/dev/null

AGE=$($V eval 'Math.round(performance.now())')
$V click "$ACTION" >/dev/null
$V sleep 3000 >/dev/null

RESULT=$($V eval '(()=>{const re=new RegExp("'"$SUCCESS"'","i");
  const appeared = re.test(document.body.innerText) && !re.test(window.__before||"");
  return (window.__hit || appeared) ? "worked" : "SWALLOWED"})()')
printf 'click at t+%-7sms after load → %s\n' "$AGE" "$RESULT"
[ "$RESULT" = "worked" ]   # exit 0 on success, 1 on discard — bisect.sh relies on this

# ── NOTE ON THE SUCCESS PATTERN ─────────────────────────────────────────────
# Make it specific to the confirmation you expect. A loose pattern like "thank you"
# matches unrelated page copy and will report a discarded action as a success — this
# script did exactly that on its first smoke test. Detection therefore requires text
# that was ABSENT before the click and PRESENT after it.
