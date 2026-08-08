#!/usr/bin/env bash
# One probe: perform the action DELAY_MS after page load, report whether it landed.
# Usage: bash probe.sh [delay_ms]        e.g. bash probe.sh 0
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"
source "$HERE/resolve_native_binary.sh"

V="${VIBIUM:-$VIBIUM_NATIVE}"
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

# Timestamp and click MUST be one eval call, not two CLI commands. Two commands means a
# separate round-trip (measured ~170-250ms on this machine) sits unaccounted-for between
# "the time we recorded" and "the click that actually reached the page" — noise on the
# same order as the boundary itself. One call means the page's own clock reads itself in
# the same tick it dispatches the click: no gap to account for.
# Trade-off: this bypasses vibium's actionability checks (visibility, scroll-into-view,
# obscured-element detection) that `$V click` normally does. Acceptable here because the
# button is already in view by this point in the flow — not acceptable if you reuse this
# pattern somewhere the target might not be interactable yet.
AGE=$($V eval "(()=>{const t=Math.round(performance.now());document.querySelector('${ACTION}').click();return t})()")
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
