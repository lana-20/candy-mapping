#!/usr/bin/env bash
# Site defect or missed click? Count the clicks the page actually receives and watch the network.
# Run this BEFORE reporting any race. Uses the CONFIG block from probe.sh.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"
source "$HERE/resolve_native_binary.sh"
V="${VIBIUM:-$VIBIUM_NATIVE}"

[ "$COLD_CACHE" = "1" ] && $V cookies clear >/dev/null
$V go "$URL" >/dev/null
if [ -n "$DISMISS" ]; then
  $V wait "$DISMISS" --state visible --timeout 10000 >/dev/null 2>&1 && $V click "$DISMISS" >/dev/null 2>&1
fi
for pair in "${FILL[@]}"; do
  sel="${pair%% :: *}"; val="${pair##* :: }"
  $V fill "$sel" "$val" >/dev/null 2>&1
  [ "$($V value "$sel" 2>/dev/null)" = "$val" ] || { echo "PRECONDITION FAILED on $sel"; exit 2; }
done

$V eval 'window.__c=0;window.__net=[];
  const of=window.fetch;window.fetch=function(...a){window.__net.push("fetch "+String(a[0]).slice(0,60));return of.apply(this,a)};
  const oo=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){window.__net.push(m+" "+String(u).slice(0,60));return oo.apply(this,arguments)};
  document.querySelector('"'$ACTION'"').addEventListener("click",()=>window.__c++,true);"armed"' >/dev/null

$V click "$ACTION" >/dev/null; $V sleep 2500 >/dev/null
echo "after click 1 → listener=$($V eval 'window.__c')  network=$($V eval 'JSON.stringify(window.__net)')"

$V click "$ACTION" >/dev/null; $V sleep 3000 >/dev/null
echo "after click 2 → listener=$($V eval 'window.__c')  network=$($V eval 'JSON.stringify(window.__net)')"

echo
echo "READ IT LIKE THIS"
echo "  listener 1, network [] then listener 2, network [request]"
echo "     → the page received the click and chose to do nothing. SITE DEFECT."
echo "  listener 0"
echo "     → the click never reached the element. Your locator is wrong. Not a race."
echo "  listener 1 with a request already sent"
echo "     → the action did fire. No race at this timing."
