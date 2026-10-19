#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$root/scripts/prepare-runtime.py"
cmake -S "$root/build/llvm-src/runtimes" -B "$root/build/ps4-runtime" -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$root/cmake/openorbis-runtime.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$root/build/ps4-deps" \
  -DLLVM_ENABLE_RUNTIMES='libcxx;libcxxabi;libunwind' \
  -DLLVM_INCLUDE_TESTS=OFF -DLLVM_INCLUDE_DOCS=OFF \
  -DLIBCXX_INCLUDE_TESTS=OFF -DLIBCXX_INCLUDE_BENCHMARKS=OFF \
  -DLIBCXX_ENABLE_SHARED=OFF -DLIBCXX_ENABLE_STATIC=ON \
  -DLIBCXX_HAS_MUSL_LIBC=ON -DLIBCXX_ENABLE_FILESYSTEM=OFF \
  -DLIBCXX_ENABLE_TIME_ZONE_DATABASE=OFF -DLIBCXX_ENABLE_RANDOM_DEVICE=OFF \
  -DLIBCXXABI_ENABLE_SHARED=OFF -DLIBCXXABI_ENABLE_STATIC=ON \
  -DLIBCXXABI_INCLUDE_TESTS=OFF -DLIBCXXABI_USE_LLVM_UNWINDER=ON \
  -DLIBUNWIND_ENABLE_SHARED=OFF -DLIBUNWIND_ENABLE_STATIC=ON \
  -DLIBUNWIND_INCLUDE_TESTS=OFF -DLIBUNWIND_IS_BAREMETAL=ON
cmake --build "$root/build/ps4-runtime" -j"${BUILD_JOBS:-8}"
cmake --install "$root/build/ps4-runtime"
