# Collection release preparation

Physical PS4 acceptance reported by maintainer on 2026-10-19.
Public release is pending the distribution checks below.

Visibility change explicitly authorized by maintainer, conditional on completion
of the release checks. Do not publish while the source inventory gate is false.
2026-10-19: user approved replacing the untraced SDK SDL_image archive. Candidate
0.07 uses unmodified upstream 2.6.3 at d3c6d5963dbe438bcae0e2b6f3d7cfea23d02829.
Other source candidates captured by scripts/prepare-release-sources.py. Packaged
OpenOrbis module hashes match the SDK's module build outputs. Old 0.06 untouched.

New test package: `Descent-I-II-PS4-Collection-0.07.pkg`.
SHA-256: `2b71a79f12ebcd7abb1089f556cbd1b82c75f094195ec0ab5ade06f1ea83e2af`.
Same launcher; relinked games require a physical PS4 retest before release.
Package extraction/hash/allowlist checks pass, including unchanged launcher.
Both games reached rendered first levels via the launcher in shadPS4, with
injected movement/yaw/fire and visually inspected screenshots. FTP delivery to
the maintainer's PS4 has a matching full-file readback hash. Neither of these
checks substitutes for physical acceptance of this new candidate.

Tested candidate: `Descent-I-II-PS4-Collection-0.06.pkg`

SHA-256: `57a60e47c087b1ff480e63bf6495b0834a83dcc9766be4a02e187feb65ef5d27`

## Release notes draft

Descent I + II PS4 Collection: one launcher with custom artwork and icon,
remembered selection, controller navigation, data availability indicators,
and missing-data guidance. Native gameplay and controls tested on physical PS4.
Game executables are unchanged from the tested 0.05 build.

No original assets, demo levels, ISOs or installers bundled. HDD data takes
priority, followed by USB0–USB7. Full classic PC data is supported by the engine
but not yet tested on this port. See GAME-DATA.txt for required files.

Music/movies disabled; multiplayer unsupported; legacy line/point drawing
incomplete. Quitting a game returns to the PS4 shell.

## Before public binary distribution

- Include full DXX-Rebirth COPYING and GPL-3 texts, not only COPYING.
- Inventory SDL, SDL_image/codecs, PhysFS, PS4GL, Vulkan/OpenGNM, shader compiler,
  LLVM runtime and packaged module origins and notices.
- Make corresponding engine/platform/dependency modifications and build scripts
  available with exact source revisions. Sibling paths and prebuilt libraries
  alone do not provide the complete source distribution.
- Audit staged sources and Git history for private data, credentials and logs.
- Visibility approval received; execute only after outstanding checks pass.
- Supply installation instructions, notices, corresponding sources and checksums
  with the verified package. Do not silently replace the tested 0.06 artifact.

Package validation: `python3 scripts/verify-collection.py --version 0.07`.
