#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
sdk=${OO_PS4_TOOLCHAIN:-/opt/openorbis/OpenOrbis/PS4Toolchain}
mkdir -p "$root/artifacts"
clang++ --target=x86_64-pc-freebsd12-elf --sysroot="$sdk" -std=c++23 \
    -D__PS4__ -D__ORBIS__ -D_LIBCPP_HAS_NO_LOCALE -nostdinc++ \
    -isystem "$sdk/include/c++/v1" -isystem "$sdk/include" \
    -fsyntax-only "$root/tests/cxx-library-probe.cpp" \
    2>&1 | tee "$root/artifacts/ps4-cxx-probe.log"
