#!/usr/bin/env bash
# Narrow the vulnerability window to a bracket between two real measurements.
# Usage: bash bisect.sh [max_delay_ms]      default sweeps to 20000
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROBE="$HERE/probe.sh"
MAX="${1:-20000}"

echo "── coarse sweep ──────────────────────────────────────────"
LAST_FAIL=-1
FIRST_PASS=-1
for d in 0 2000 5000 10000 "$MAX"; do
  [ "$d" -gt "$MAX" ] && continue
  if bash "$PROBE" "$d"; then
    FIRST_PASS=$d; break
  else
    LAST_FAIL=$d
  fi
done

if [ "$FIRST_PASS" -lt 0 ]; then
  echo; echo "No delay up to ${MAX}ms let the action through."
  echo "Either the window is wider than the sweep, or the action is broken outright — not a race."
  exit 0
fi
if [ "$LAST_FAIL" -lt 0 ]; then
  echo; echo "The action landed at zero delay. No race present; nothing to bisect."
  exit 0
fi

echo
echo "── bisect between ${LAST_FAIL}ms and ${FIRST_PASS}ms ─────"
while [ $(( FIRST_PASS - LAST_FAIL )) -gt 400 ]; do
  MID=$(( (LAST_FAIL + FIRST_PASS) / 2 ))
  if bash "$PROBE" "$MID"; then FIRST_PASS=$MID; else LAST_FAIL=$MID; fi
done

echo
echo "── result ────────────────────────────────────────────────"
echo "  discarded at a delay of ${LAST_FAIL}ms · landed at ${FIRST_PASS}ms"
echo
echo "  NOTE: those are delays, not clock times. Read the actual t+ values printed"
echo "  above and quote the window as the bracket between the last discarded click"
echo "  and the first successful one. Confirm both edges twice before reporting."
