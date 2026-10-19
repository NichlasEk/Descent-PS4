# Descent PS4 0.07 source and relinking companion

This archive accompanies the maintainer-tested 0.07 PKG. No original game data
is included. Keep the license texts and source companion with redistributions.

Requirements: Linux, Python 3, Clang/LLD/LLVM tools, and an installed OpenOrbis
SDK (tested with v0.5.3 LLVM18 distribution). Set `OO_PS4_TOOLCHAIN` to its root.
The package is homebrew, not a signed Sony retail application.

From the extracted companion directory:

```sh
export OO_PS4_TOOLCHAIN=/path/to/OpenOrbis/PS4Toolchain
python3 build.py                  # relink the supplied tested objects
python3 build.py --rebuild --jobs 4 # recompile engine/platform/PS4GL and relink
```

Outputs go to `relinked/` or `rebuilt/`; supplied objects are not overwritten.
Edit source files in `sources/engine`, `sources/ps4gl`, or `port-source/platform`
before rebuilding. Compiler/link plans are in BUILD.json. SDK paths are expanded
at runtime; the author's private sibling checkout is not needed for these steps.
Sign modified ELFs with OpenOrbis create-fself and package them using the included
port packaging scripts adapted to the new binaries. The original PKG is never
silently replaced by these build commands.

`sources/` contains dependency source snapshots with local changes applied and
original notices retained; `INVENTORY.json` records source revisions and hashes.
`build-reference/` preserves dependency build recipes and patches. Runtime21
source, installed generated headers, and generated engine control tables are
included. `port-source/` contains the port repository at release assembly time.

The quick rebuild command uses the captured dependency archives. Their source
and build recipes are supplied for modification; it does not claim to rebuild
the entire SDK or every dependency in one command. System runtime/firmware
services remain external. Historical SDK musl/compiler-rt source is identified
as reference material, not a bit-reproducible proof of the installed SDK.

For the native GPU dependencies, with Python codegen requirements from
`build-reference/psbc-codegen-requirements.txt` installed:

```sh
make -C sources/opengnm CC=clang AR=llvm-ar -j4
make -C sources/opengnm-psbc -f Makefile.orbis -j4
make -C sources/vulkan-ps4 -f Makefile.orbis libvulkan_ps4.a -j4
```

These produce new archives inside the source trees, not inside `libraries/`.
To use modified libraries, update the corresponding archive argument in BUILD.json
or replace its captured archive. PSBC must retain the C11 thread-symbol namespacing
shown in build-reference/build-scummvm-vulkan.sh; the shipped archive has that
transformation applied. SDL and glslang build references describe their private
adapter/symbol transformations too. Their original project-root paths need adapting
to this companion's `sources/` layout; do not run the reference scripts blindly.

See port-source/docs/THIRD-PARTY.md and licenses/. Descent/Parallax restrictions
and upstream's GPLv3 exception apply; this is not a blanket MIT project.
