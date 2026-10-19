#!/usr/bin/env bash
# Pinned SDL_image, compiled locally; never modifies the installed SDK.
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
sdk=${OO_PS4_TOOLCHAIN:-/opt/openorbis/OpenOrbis/PS4Toolchain}
src="$root/build/sdl-image-src"
revision=d3c6d5963dbe438bcae0e2b6f3d7cfea23d02829
if [[ ! -d "$src/.git" ]]; then
    git clone --no-checkout https://github.com/libsdl-org/SDL_image.git "$src"
    git -C "$src" checkout --detach "$revision"
fi
[[ $(git -C "$src" rev-parse HEAD) == "$revision" ]]
[[ -z $(git -C "$src" status --porcelain) ]]
out="$root/build/ps4-image"
mkdir -p "$out"
objects=()
for source in "$src"/IMG*.c; do
    object="$out/$(basename "$source" .c).o"
    clang --target=x86_64-pc-freebsd12-elf --sysroot="$sdk" -fPIC -O2 \
        -D__PS4__ -D__ORBIS__ -D_BSD_SOURCE -D_GNU_SOURCE \
        -DUSE_STBIMAGE -DLOAD_PNG -DLOAD_JPG -DLOAD_BMP -DLOAD_GIF \
        -DLOAD_LBM -DLOAD_PCX -DLOAD_PNM -DLOAD_QOI -DLOAD_SVG -DLOAD_TGA \
        -DLOAD_XCF -DLOAD_XPM -DLOAD_XV \
        -isystem "$sdk/include" -I"$sdk/include/SDL2" -I"$src" \
        -c "$source" -o "$object"
    objects+=("$object")
done
llvm-ar rcs "$out/libSDL2_image.a" "${objects[@]}"
echo "SDL_image 2.6.3: $revision"
sha256sum "$out/libSDL2_image.a"
