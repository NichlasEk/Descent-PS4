# Third-party components and source companion

This is an unofficial port. Descent and its original data remain associated
with their respective rights holders. No original game data is distributed.

| Component | Source and notices |
| --- | --- |
| Descent / DXX-Rebirth | Revision in UPSTREAM.md; LICENSE and licenses/GPL-3.txt; Parallax terms plus GPLv3 contributions with upstream exception |
| Port integration | Nichlas Ek; see root LICENSE |
| PS4GL | Nichlas Ek; MIT alternative in source directory LICENSE.MIT and LICENSING.md |
| PhysFS | 3.2.0, revision eb3383b532c5f74bfeb42ec306ba2cf80eed988c; zlib-style LICENSE.txt; local OpenOrbis patch |
| SDL-PS4 | 7774cf3e7d04448c44d569c50d1f9a4532a2efe7; COPYING.txt; patched joystick and PS4GL video integration |
| SDL_image (0.07) | Upstream 2.6.3, d3c6d5963dbe438bcae0e2b6f3d7cfea23d02829; unmodified source, local build; LICENSE.txt and embedded codec source notices included in PKG |
| OpenGNM / Vulkan-PS4 | MIT plus retained per-file notices; modified source snapshots recorded in private inventory |
| OpenGNM PSBC | MIT and Mesa/per-file notices; shader compiler source; C11 thread symbols privately renamed |
| glslang | fa9c3deb49e035a8abcabe366f26aac010f6cbfb; LICENSE.txt and per-file permissive notices; patched PS4 build |
| LLVM runtime | 21.1.8; Apache-2.0 with LLVM exceptions; component LICENSE.TXT files; project-local patches |
| OpenOrbis modules | SDK GPLv3 modules, not firmware dumps; packaged bytes checked against SDK source-build outputs |
| Gontserrat font | OFL; assets/launcher/FONT-LICENSE.txt |
| Launcher art/icon | Generated for this port; prompts retained in assets/launcher/PROMPTS.txt; no trademark rights asserted |

`scripts/prepare-release-sources.py` records source snapshots, per-file hashes
and Git revisions where available. Assembly subsequently verifies the portable
core-source build, byte-identical relinks and distribution contents. The final
companion contains BUILD.json, build.py and a per-file manifest. No full SDK
bit-reproducibility claim is made; historical SDK runtime sources are marked as
references. See SOURCE-COMPANION.md for build instructions and limits.

The complete source and notice companion accompanies this binary release.
Preserve both when redistributing. The tested 0.07 PKG is unchanged.

0.07 replaces only the SDK SDL_image link input in the two games, reusing the
existing game/platform objects and other link inputs. The 0.06 launcher SELF is
preserved byte-for-byte. PNG/JPEG use the bundled stb_image backend, avoiding
additional untracked codec libraries; native simple-format decoders are enabled.
Build script: scripts/build-ps4-image.sh. This resolves the image-source gap for
0.07, not retroactively for the old SDK archive in 0.06. The maintainer has now
confirmed 0.07 works well on physical PS4.
