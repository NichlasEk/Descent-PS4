#!/usr/bin/env bash
# Headless startup evidence only: not gameplay, audio or PS4 acceptance.
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
game=${1:-d1}
case "$game" in d1) number=1;; d2) number=2;; *) exit 2;; esac
mkdir -p "$root/build/profiles/$game" "$root/artifacts"
export D1X_REBIRTH_HOME="$root/build/profiles/d1"
export D2X_REBIRTH_HOME="$root/build/profiles/d2"
export SDL_AUDIODRIVER=dummy
export SDL_VIDEODRIVER=x11
export GDK_BACKEND=x11
xvfb-run -a -s '-screen 0 1280x720x24' bash -c '
  root=$1; game=$2; number=$3
  timeout -k 3 12 "$root/build/linux/d${number}x-rebirth/d${number}x-rebirth" \
    -hogdir "$root/media/demo/$game" -window -notitles -nomovies -nomusic \
    > "$root/artifacts/$game-host-smoke.log" 2>&1 &
  task_pid=$!
  sleep 7
  import -window root "$root/artifacts/$game-host-smoke.png"
  wait "$task_pid"
  status=$?
  [[ "$status" == 0 || "$status" == 124 || "$status" == 137 ]] || exit "$status"
  if rg -i "error:|double free|dumped core|AddressSanitizer" "$root/artifacts/$game-host-smoke.log"; then
    exit 1
  fi
' bash "$root" "$game" "$number"
echo "Captured $game startup; inspect screenshot/log before judging success."
