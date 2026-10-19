#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
sdk=${OO_PS4_TOOLCHAIN:-/opt/openorbis/OpenOrbis/PS4Toolchain}
mkdir -p "$root/build/ps4-probes"
clang++ --target=x86_64-pc-freebsd12-elf --sysroot="$sdk" -std=c++23 \
  -fPIC -D__PS4__ -D__ORBIS__ -D_BSD_SOURCE -D_GNU_SOURCE -nostdinc++ \
  -isystem "$root/build/ps4-deps/include/c++/v1" -isystem "$sdk/include" \
  -fuse-ld=lld -nostdlib -Wl,-pie,--eh-frame-hdr,-z,max-page-size=0x4000 \
  -Wl,--script="$sdk/link.x" "$sdk/lib/crt1.o" \
  "$root/tests/cxx-runtime-probe.cpp" \
  -L"$root/build/ps4-deps/lib" -L"$sdk/lib" \
  -lc++ -lc++abi -lunwind -lc -lkernel \
  -o "$root/build/ps4-probes/cxx-runtime.elf"
