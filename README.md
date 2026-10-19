# Descent I & II — OpenOrbis PS4

Native PS4 port project by [Nichlas Ek](https://github.com/NichlasEk), based on
[DXX-Rebirth](https://github.com/dxx-rebirth/dxx-rebirth).

**Collection 0.07: confirmed working on physical PS4 by the maintainer.**

[Download v0.07](https://github.com/NichlasEk/Descent-PS4/releases/tag/v0.07).
The distribution ZIP contains the tested PKG, installation instructions and
licenses. The separate source/relink companion is for developers.

Both engines now run natively on PS4, with a shared illustrated launcher and
controller support. See [release preparation](docs/RELEASE.md) and
[current handoff](HANDOFF.md) for evidence and remaining limitations.

Supply your own classic PC game files or separately obtained official demos.
Data is read from `/data/descent-ps4/d1/data` and `d2/data` first, then
`/mnt/usb0/descent-ps4/d1/data` and `d2/data`, through USB7. Existing HDD demos
take priority over USB retail data. Profiles stay on HDD. No game data is bundled.
See [required files and upgrading to full games](docs/GAME-DATA.txt).
Retail data is supported by the engine but not yet tested on this port.

Launcher: D-pad/left stick selects, Cross starts, Triangle shows help, Circle exits.
Flight: left stick moves/strafes, right stick aims, R2/L2 fire, L1/R1 roll.
Quitting a game returns to the PS4 shell. Music/movies are disabled; multiplayer
is unsupported; legacy lines/points (automap/crosshair) need further work.

The repository's original build scripts use sibling ScummVM-PS4 dependencies.
For an independent build, use the release's relocatable source/relink companion:
all engine/platform/PS4GL objects can be recompiled without that sibling checkout.
Dependency source and build references are also included; the quick build uses
captured dependency archives. See [build scope](docs/SOURCE-COMPANION.md).

The upstream engine supports Descent I shareware and Descent II demo data.
Those files remain local and separate from source, even when freely downloadable.
See upstream [installation instructions](https://github.com/dxx-rebirth/dxx-rebirth/blob/master/INSTALL.markdown).

The existing AvP port is a reference for PS4 platform integration, not a
replacement for validating Descent's own renderer and runtime requirements.
The shared graphics implementation is Nichlas Ek's ps4gl, available under MIT.

## Layout

- `engine/`: pinned upstream checkout, excluded from this port's Git history.
- `patches/`: reproducible upstream modifications when needed.
- `platform/`: PS4-specific integration when implemented.
- `scripts/`: source/data preparation and build helpers.
- `build/`, `media/`, `artifacts/`, `dist/`: local-only inputs and outputs.

## Initial host build

Install a modern C++ compiler, SDL2, SDL2_mixer, SDL2_image, PhysFS 3, libpng,
OpenGL/GLU development libraries, Python 3 and uv, then run:

```sh
bash scripts/build-linux.sh
```

This downloads the pinned engine and shareware/demo data for local tests only.
It installs SCons into a project-local environment, not system Python.
See [source/data pins](docs/UPSTREAM.md).

Upstream Descent and DXX-Rebirth code retains its own licensing and credits.
No blanket MIT/GPL claim is made for the combined project. See [licenses and
credits](docs/THIRD-PARTY.md). Retail assets are never included.
