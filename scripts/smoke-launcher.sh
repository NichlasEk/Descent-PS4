#!/usr/bin/env bash
# Capture is evidence to inspect, not an automatic gameplay PASS.
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
mode=${1:-menu}
case "$mode" in menu|help|d1|d2) ;; *) exit 2;; esac
export LAUNCHER_MODE="$mode"
export LAUNCHER_STAGE
LAUNCHER_STAGE=$(python3 -c 'import json,sys; print(json.load(open("dist/Descent-I-II-PS4-Collection-"+sys.argv[1]+".manifest.json"))["stage"])' "${COLLECTION_VERSION:-0.06}")
export XDG_DATA_HOME="${LAUNCHER_PROFILE:-$root/build/emulator-profile}" SDL_VIDEODRIVER=x11
export DESCENT_SHADPS4=${SHADPS4:-/home/nichlas/shadPS4/build-validation/shadps4}
cc tests/launcher-input.c $(pkg-config --cflags --libs x11 xtst) -o build/launcher-input
if [[ ${COLLECTION_PLAYTEST:-0} == 1 ]]; then
    cc tests/emulator-accept.c $(pkg-config --cflags --libs x11 xtst) -o build/emulator-accept
fi
timeout -k 3 60 xvfb-run -a -s '-screen 0 1280x720x24' bash -c '
    setsid "$DESCENT_SHADPS4" --fullscreen false "$LAUNCHER_STAGE/eboot.bin" > "artifacts/launcher-$LAUNCHER_MODE.log" 2>&1 &
    app_pid=$!
    trap '\''kill -- -"$app_pid" 2>/dev/null || true'\'' EXIT
    sleep 12
    case "$LAUNCHER_MODE" in
        help) build/launcher-input c;;
        d1) build/launcher-input Left n;;
        d2) build/launcher-input Right n;;
    esac
    sleep 12
    if [[ ${COLLECTION_PLAYTEST:-0} == 1 ]]; then
        build/emulator-accept
    fi
    import -window root "artifacts/launcher-$LAUNCHER_MODE.png"
    kill -- -"$app_pid" 2>/dev/null || true
    wait "$app_pid" || true
'
