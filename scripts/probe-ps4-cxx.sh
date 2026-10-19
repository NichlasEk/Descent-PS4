#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
sdk=${OO_PS4_TOOLCHAIN:-/opt/openorbis/OpenOrbis/PS4Toolchain}
headers="$root/build/ps4-deps/include/c++/v1"
if [[ ! -f "$headers/__config_site" ]]; then
    echo 'Build the isolated runtime first: bash scripts/build-ps4-runtime.sh' >&2
    exit 1
fi
mkdir -p "$root/artifacts"
clang++ --target=x86_64-pc-freebsd12-elf --sysroot="$sdk" -std=c++23 \
    -D__PS4__ -D__ORBIS__ -nostdinc++ \
    -isystem "$headers" -isystem "$sdk/include" \
    -fsyntax-only "$root/tests/cxx-library-probe.cpp" \
    2>&1 | tee "$root/artifacts/ps4-cxx-probe.log"
