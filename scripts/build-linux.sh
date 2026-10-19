#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
python3 scripts/prepare.py
if [[ ! -x build/tools/bin/scons ]]; then
    uv venv build/tools
    uv pip install --python build/tools/bin/python scons==4.10.1
fi
mkdir -p artifacts
build/tools/bin/scons -C engine -j"${BUILD_JOBS:-8}" sdl2=1 sdlmixer=1 \
    builddir=../build/linux ../build/linux "$@" 2>&1 | tee artifacts/build-linux.log
