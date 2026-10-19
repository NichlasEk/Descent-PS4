#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
mkdir -p build/launcher-assets
cc tools/make-menu-font.c $(pkg-config --cflags --libs freetype2) -o build/make-menu-font
build/make-menu-font assets/launcher/menu.ttf build/launcher-assets/font.bin
magick assets/launcher/hangar.png -resize '1280x720!' -alpha on -depth 8 RGBA:build/launcher-assets/hangar.rgba
cmake -S . -B build/ps4-game -G Ninja -DCMAKE_TOOLCHAIN_FILE="$root/cmake/openorbis-runtime.cmake"
cmake --build build/ps4-game --target descentlauncher -j8
