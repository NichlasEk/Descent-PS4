#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
mkdir -p artifacts build
python3 scripts/prepare.py
physfs_commit=eb3383b532c5f74bfeb42ec306ba2cf80eed988c
if [[ ! -d build/physfs-src/.git ]]; then
    git clone --depth 1 --branch release-3.2.0 https://github.com/icculus/physfs.git build/physfs-src
fi
[[ $(git -C build/physfs-src rev-parse HEAD) == "$physfs_commit" ]]
patch="$root/dependency-patches/physfs-openorbis.patch"
if ! git -C build/physfs-src apply --reverse --check "$patch" 2>/dev/null; then
    git -C build/physfs-src apply --check "$patch"
    git -C build/physfs-src apply "$patch"
fi
if [[ ! -x build/tools/bin/scons ]]; then
    uv venv build/tools
    uv pip install --python build/tools/bin/python scons==4.10.1
fi
# SCons supplies the upstream source graph and generated control-navigation
# tables. Target compilation uses our reviewed PS4 config and headers, not
# host libraries, objects, architecture flags or linker options.
build/tools/bin/scons -C engine CXX=clang++ sdl2=1 sdlmixer=0 sdlimage=1 \
    use_udp=1 use_tracker=0 ipv6=0 screenshot=none use_stereo_render=0 lto=0 \
    builddir=../build/ps4-plan compilation_database=../build/ps4-plan/compile_commands.json \
    ../build/ps4-plan/compile_commands.json ../build/ps4-plan/dxxsconf.h \
    ../build/ps4-plan/d1x-rebirth/kconfig.udlr.h ../build/ps4-plan/d2x-rebirth/kconfig.udlr.h
bash scripts/build-ps4-runtime.sh
cmake -S build/physfs-src -B build/ps4-physfs -G Ninja \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_TOOLCHAIN_FILE="$root/cmake/openorbis-runtime.cmake" \
    -DPHYSFS_BUILD_SHARED=OFF -DPHYSFS_BUILD_TEST=OFF -DPHYSFS_BUILD_DOCS=OFF
cmake --build build/ps4-physfs -j"${BUILD_JOBS:-8}"
python3 scripts/compile-ps4-engine.py
cmake -S . -B build/ps4-game -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$root/cmake/openorbis-runtime.cmake"
cmake --build build/ps4-game -j"${BUILD_JOBS:-8}"
