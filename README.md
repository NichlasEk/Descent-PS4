# Descent I & II — OpenOrbis PS4

Native PS4 port project by [Nichlas Ek](https://github.com/NichlasEk), based on
[DXX-Rebirth](https://github.com/dxx-rebirth/dxx-rebirth).

**Initial bring-up: no PS4 executable or console compatibility claim yet.**

First milestone: a Descent I shareware level with rendering, audio and controls.
Then bring up Descent II using the same platform layer. Planned data policy:
external HDD first, USB fallback; no retail game data in packages or Git.

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
No blanket MIT/GPL claim is made for the combined project. Distribution terms
will be reviewed before a binary release; retail assets are never included.
