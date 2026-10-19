# Component inventory (release review in progress)

This is an unofficial port. Descent and its original data remain associated
with their respective rights holders. No original game data is distributed.

| Component | Source and notices |
| --- | --- |
| Descent / DXX-Rebirth | Revision in UPSTREAM.md; LICENSE and licenses/GPL-3.txt; Parallax terms plus GPLv3 contributions with upstream exception |
| Port integration | Nichlas Ek; see root LICENSE |
| PS4GL | Nichlas Ek; MIT alternative in source directory LICENSE.MIT and LICENSING.md |
| PhysFS | 3.2.0, revision eb3383b532c5f74bfeb42ec306ba2cf80eed988c; zlib-style LICENSE.txt; local OpenOrbis patch |
| SDL-PS4 | 7774cf3e7d04448c44d569c50d1f9a4532a2efe7; COPYING.txt; patched joystick and PS4GL video integration |
| SDL_image | SDK archive reports development version 2.0.6; exact corresponding source not yet identified; release gate remains closed |
| OpenGNM / Vulkan-PS4 | MIT plus retained per-file notices; modified source snapshots recorded in private inventory |
| OpenGNM PSBC | MIT and Mesa/per-file notices; shader compiler source; C11 thread symbols privately renamed |
| glslang | fa9c3deb49e035a8abcabe366f26aac010f6cbfb; LICENSE.txt and per-file permissive notices; patched PS4 build |
| LLVM runtime | 21.1.8; Apache-2.0 with LLVM exceptions; component LICENSE.TXT files; project-local patches |
| OpenOrbis modules | SDK GPLv3 modules, not firmware dumps; packaged bytes checked against SDK source-build outputs |
| Gontserrat font | OFL; assets/launcher/FONT-LICENSE.txt |
| Launcher art/icon | Generated for this port; prompts retained in assets/launcher/PROMPTS.txt; no trademark rights asserted |

`scripts/prepare-release-sources.py` snapshots source candidates and records
per-file hashes and Git revisions where available. It deliberately records
`public_release_ready: false`. Its build references are not yet a standalone
reproducible build. Source snapshots do not establish that every prebuilt
dependency corresponds exactly to those sources.

The complete source and notice companion must accompany a future public binary
release. The tested 0.06 PKG is unchanged while this review is performed.
