# Upstream and data pins

Engine: https://github.com/dxx-rebirth/dxx-rebirth

Revision: `6943b924bea749543ef5729f31a28345e79716d2`.
Modern upstream requires selected C++23 features and PhysFS 3.x. The local host
has PhysFS 3.2.0, SDL2 and SDL2_mixer. PS4 compiler/library compatibility must be
checked independently; a successful Linux build is not a PS4 build.

Source licensing is described by upstream `COPYING.txt` and `GPL-3.txt`:
original Parallax terms plus GPLv3 contributions with an explicit exception for
conflicts with the original Parallax license. Preserve the exact texts when
distributing source or binaries. This is not an unrestricted GPL-only engine.

Local demo data comes from the URLs linked by upstream INSTALL.markdown:

| Archive | SHA-256 |
| --- | --- |
| https://icculus.org/d2x/data/desc14sw.tar.gz | `8b65eda01d03401d7a2dc71976528fbb7e0b07a93ce8ee0a9f1d9103623ae249` |
| https://icculus.org/d2x/data/d2shar10.tar.gz | `65e8dc58dc7fdc09696f9a06c814ef81f8026b330976a2dced3347895814a4af` |

These hashes pin the archives retrieved on 2026-10-19; they are locally computed,
not publisher-signed checksums. The preparation script extracts only the five
engine data files, not original DOS executables, and refuses differing existing
files. Demo data is not committed or bundled for public distribution. Review
the archives' redistribution terms before any future bundled demo release.
