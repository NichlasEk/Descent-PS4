#!/usr/bin/env bash
# Bounded emulator startup capture, NOT a gameplay acceptance test.
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
game=${1:-1}
case "$game" in 1|2) ;; *) exit 2;; esac
export OO_PS4_TOOLCHAIN=${OO_PS4_TOOLCHAIN:-/opt/openorbis/OpenOrbis/PS4Toolchain}
runtime="$root/build/runtime-d$game"
profile="$root/build/emulator-profile"
mkdir -p "$runtime/sce_module" "$profile/shadPS4/data/descent-ps4/d$game" artifacts
"${CREATE_FSELF:-/home/nichlas/ut99-orbis/build/create-fself-current}" \
    -in="$root/build/ps4-game/descent$game" -out="$runtime/descent$game.oelf" \
    --eboot "$runtime/eboot.bin" --paid 0x3800000000000011
cp "$OO_PS4_TOOLCHAIN/samples/hello_world/sce_module/libc.prx" \
   "$OO_PS4_TOOLCHAIN/samples/hello_world/sce_module/libSceFios2.prx" "$runtime/sce_module/"
data="$profile/shadPS4/data/descent-ps4/d$game/data"
if [[ ! -e "$data" && ! -L "$data" ]]; then ln -s "$root/media/demo/d$game" "$data"; fi
export XDG_DATA_HOME="$profile" SDL_VIDEODRIVER=x11
export DESCENT_SMOKE_GAME="$game" DESCENT_SMOKE_RUNTIME="$runtime"
export DESCENT_SHADPS4=${SHADPS4:-/home/nichlas/shadPS4/build-validation/shadps4}
if [[ ${DESCENT_SMOKE_ACCEPT:-0} == 1 ]]; then
    cc tests/emulator-accept.c $(pkg-config --cflags --libs x11 xtst) -o build/emulator-accept
fi
timeout -k 3 45 xvfb-run -a -s '-screen 0 1280x720x24' bash -c '
    "$DESCENT_SHADPS4" --fullscreen false "$DESCENT_SMOKE_RUNTIME/eboot.bin" \
        > "artifacts/d$DESCENT_SMOKE_GAME-ps4-smoke.log" 2>&1 &
    app_pid=$!
    trap '\''kill "$app_pid" 2>/dev/null || true'\'' EXIT
    if [[ ${DESCENT_SMOKE_ACCEPT:-0} == 1 ]]; then
        sleep 10
        build/emulator-accept || exit $?
    else
        sleep 20
    fi
    import -window root "artifacts/d$DESCENT_SMOKE_GAME-ps4-smoke.png"
    kill "$app_pid" 2>/dev/null || true
    wait "$app_pid" || true
'
echo 'Capture only: inspect screenshot, boot.log and emulator errors before calling it a pass.'
