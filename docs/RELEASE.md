# Descent I + II PS4 — v0.07

The maintainer reports Collection 0.07 works very well on physical PS4.
This release uses that exact package, not a newly rebuilt replacement.

Package: `Descent-I-II-PS4-Collection-0.07.pkg` (74,514,432 bytes).
SHA-256: `2b71a79f12ebcd7abb1089f556cbd1b82c75f094195ec0ab5ade06f1ea83e2af`.

## Included

- One illustrated launcher for both games, remembered selection and controller navigation.
- Controller flight/combat bindings and HDD-first, USB0–USB7 data lookup.
- Original launcher artwork/icon; no original game data, demo levels or installers.
- Pinned, locally built SDL_image 2.6.3 instead of the untraced SDK archive.
- Installation instructions, licenses and a separate source/relink companion.

Download the distribution ZIP and extract its PKG for installation. Supply your
own classic PC game files or separately obtained official demo/shareware files;
see GAME-DATA.txt. This is unofficial homebrew, not a Sony retail release.
Original Parallax non-commercial terms and upstream licensing remain applicable.

## Verification

The PKG passes structural/hash checks and extracted payload allowlist verification.
Its launcher matches the previously tested 0.06 launcher byte-for-byte.
Both games reached rendered first levels through the launcher in shadPS4, with
movement/yaw/fire input inspected visually. Full FTP readback matched the local
package, followed by the maintainer's physical PS4 acceptance.

The source companion relinks all three ELFs byte-identically using captured
inputs. All 242 engine/platform/PS4GL translation units also compile from the
relocatable companion and link successfully. OpenGNM, PSBC and Vulkan archives
were independently rebuilt from the included snapshots. These verification
builds do not replace the console-tested package.

The quick source build uses supplied dependency archives; source and reference
recipes for modifying those dependencies accompany them. A full reproducible
SDK build is not claimed. See SOURCE-COMPANION.md for the exact build scope.

## Known limitations

- Music and movies disabled; multiplayer unsupported.
- Legacy line/point drawing remains incomplete (automap/crosshair).
- Exiting a game returns to the PS4 shell, not the launcher.
- Retail classic PC files are supported by the engine, but retail data has not
  yet been tested on this port; ISO/installer files must be extracted first.
- HDD/USB fallback is implemented but not exhaustively tested on hardware.

Package verification: `python3 scripts/verify-collection.py --version 0.07`.
