# Descent PS4 bring-up — 2026-10-19

## Published: v0.07 (supersedes preparation states below)

Repository is PUBLIC: https://github.com/NichlasEk/Descent-PS4
Release is published, non-draft/non-prerelease, marked latest:
https://github.com/NichlasEk/Descent-PS4/releases/tag/v0.07
Release target: 0bf002f159cc6ebfefe2de6c017e53cefa2d96e0.
Anonymous GitHub API confirms public repository and visible release assets.

Local release: dist/release-v0.07. Distribution ZIP is 73,962,275 bytes, SHA256
815079027c435316313def4350623d2816448581174a926c371b1e4152449048.
Source/relink tar.gz is 119,696,395 bytes, SHA256
a01791957ea1ff8eb66482c461d3a3cb181c2e7db05d100d14c4a86ad2d0b912.
Also attached GAME-DATA.txt and SHA256SUMS. Full GitHub download/readback passed,
and downloaded SHA256SUMS was byte-compared with local sums before publication.
32,960 companion files validated; ZIP contents read back and hashed. PKG inside
ZIP is the exact user-accepted 0.07; no original game data bundled anywhere.
All working-tree/history bounded signature/type audits passed. Full SDK binary
reproducibility is not claimed; source build scope documented in companion.
No further physical test is needed for the unchanged release container contents.

## Latest: 0.07 accepted; public release assembly

User reports 0.07 works very well on physical PS4. Conditional public-release
authorization already given. Preserve exact tested PKG hash below.
Companion build/release-sources-l5w0a7lr contains full text source snapshots
(extension allowlist fixed: valptridx.tcc and other build inputs retained),
runtime generated headers, engine generated control tables, 242 uniquely named
object inputs, captured libraries and portable BUILD.json/build.py.
All three relinks are byte-identical to original 0.07 ELFs. Core-source rebuild
(242 engine/platform/PS4GL units) and links passed. OpenGNM, PSBC, Vulkan source
builds also passed; snapshot source hashes unchanged after building. Logs under
artifacts/release-*-build.log and release-companion-rebuild.log. These rebuilt
ELFs/archives are verification only, NOT replacements for the tested package.
Next: assemble distribution ZIP/source companion, full readback/audit, commit,
draft release/upload verification, then visibility public and release publish.
No need for another physical test if the accepted PKG stays byte-identical.

## Latest: source-traced image library candidate 0.07

User explicitly approved replacing the untraced image library and making a new
test PKG. SDL_image 2.6.3, commit d3c6d5963dbe438bcae0e2b6f3d7cfea23d02829,
is now built unmodified by scripts/build-ps4-image.sh. PNG/JPEG use bundled stb;
simple-format decoders enabled. No installed SDK/sibling files modified.
Archive SHA256: 08ba557e8ca47306d43ee41d467673fffde6c4e3fcfa584207274bc06d05cf66.

scripts/relink-image-candidate.py reused the tested game/platform objects and
other link inputs, changing only SDL_image and the output path. Old game ELFs
remain in build/ps4-game, new ones in build/ps4-release007; provenance.json records
link arguments/input hashes. Original 0.06 PKG still matches its accepted hash.
Launcher SELF in 0.07 is byte-identical to 0.06. No control/gameplay changes.

Package: dist/Descent-I-II-PS4-Collection-0.07.pkg (74,514,432 bytes).
SHA256: 2b71a79f12ebcd7abb1089f556cbd1b82c75f094195ec0ab5ade06f1ea83e2af.
Stage: build/runtime-pkg-o__n_y67. ID DSNT00004, version 00.07.
Full FTP upload/readback verified at 192.168.32.229:2121:
/data/pkg/Descent-I-II-PS4-Collection-0.07.pkg.
Receipt: artifacts/ftp-Descent-I-II-PS4-Collection-0.07.json.
Old remote package and all game data/profiles left untouched; not installed.

PKG validator and scripts/verify-collection.py --version 0.07 pass: extracted
payload hashes, allowlist, SFO, no game data, unchanged launcher. GPL-3 plus
SDL_image and embedded codec notices included. Both launcher->game transitions
reached first-level cockpit/3D views in shadPS4; injected forward/yaw/fire input
gave rotated scenes, projectile impacts and energy99. Visually inspected current
artifacts/launcher-d1.png and launcher-d2.png. D2 log confirms descent2.bin.
Do not mistake older missing-data image viewed while test was running for the
completed test. Script outputs were checked after completion.

Run test: COLLECTION_VERSION=0.07 COLLECTION_PLAYTEST=1 DESCENT_SMOKE_MOVE=1
bash scripts/smoke-launcher.sh d1 (then d2). Harness uses isolated Xvfb/profile.
New private source inventory: build/release-sources-j90xigxx, includes SDL_image.
Image-source gap resolved for 0.07. Remaining gates: user physical 0.07 retest,
complete source/build companion integration and distribution review. Repository
must remain private until those pass; permission to publish then already given.
Ask user to test both games, flight/fire, audio and exit/relaunch on PS4.

## Release preparation (latest)

Maintainer now reports Collection 0.06 works very well on physical PS4 and asks
for a release. This supersedes pending launcher acceptance below. README updated;
release notes/checklist in docs/RELEASE.md. Public distribution still needs
dependency/source closure and complete notices. Repository currently private;
visibility approval received, conditional on completing release checks. Tested
package unchanged. Source candidate snapshot: build/release-sources-dzwl44ck.
Inventory's public_release_ready=false: exact SDK SDL_image source unresolved
(IMG_Linked_Version disassembly reports development 2.0.6; no upstream tag),
and dependency build integration remains incomplete. OpenOrbis packaged module
hashes verified against SDK src/modules outputs. Do not infer missing source
identity from version numbers or from a nearby upstream release.

## Latest: combined launcher 0.06 (2026-10-19)

User explicitly confirmed 0.05 game rendering AND controls work very well on
physical PS4. Preserve those tested game binaries. They now request one combined
cool launch menu and acceptance of legally purchased full classic PC game data.

Implemented Collection launcher with generated hangar art and icon, animated
selection border, D-pad/left-stick navigation, Cross launch, Triangle help,
Circle exit, remembered selection, HDD/USB data-found status and missing-data
warning instead of attempting a doomed launch. One new title DSNT00004.
Individual games currently still quit to PS4 shell, not back to launcher.

Build: `bash scripts/build-launcher.sh` (does not rebuild game engines).
Package: `python3 scripts/package-runtime.py --collection`.
Artifact: `dist/Descent-I-II-PS4-Collection-0.06.pkg`.
Uploaded and full-readback verified at 192.168.32.229:2121:
`/data/pkg/Descent-I-II-PS4-Collection-0.06.pkg` (73,203,712 bytes).
SHA-256: 57a60e47c087b1ff480e63bf6495b0834a83dcc9766be4a02e187feb65ef5d27.
Not installed by agent. Receipt: artifacts/ftp-Descent-I-II-PS4-Collection-0.06.json.
Verifier: `python3 scripts/verify-collection.py` extracts the PKG, checks payload
hashes/allowlist/SFO semantics and extracts both old 0.05 packages to prove
`descent1.bin` and `descent2.bin` are byte-identical to their tested EBOOTs.
PkgTool adds PUBTOOLINFO/PUBTOOLVER; these are the only allowed SFO additions.
No demo or retail game data in the collection PKG.

Emulator checks completed: menu screenshot, both game buttons invoke
sceSystemServiceLoadExec and reach the respective pilot menu, help overlay,
remembered last choice, missing-data refusal under a separate empty profile.
An initial cold empty-profile capture stalled before completing GPU init;
the immediate repeat reached the menu and refusal correctly. No game code
changed to work around that isolated emulator observation.
Menu/grouped glyph rendering uses the same PS4GL backend as the tested games.
Smoke harness uses an isolated process group so emulator self-restarts do not
leave an orphan game process. `bash scripts/smoke-launcher.sh menu|help|d1|d2`.
The d1 artifact was overwritten by the later missing-data test; the successful
D1 launch was visually inspected before that overwrite. D2 image retained.

Game data: `docs/GAME-DATA.txt` lists full D1/D2 PC files and explains upgrading
from demo, lower-case filenames, HDD preference and USB0-7 fallback. Engine
retail support confirmed against pinned INSTALL.markdown and file-selection
source; no retail assets available/tested yet. Music/movies remain disabled in
the unchanged games. Never equate original-game compatibility with a completed
physical retail-data test.

Art: assets/launcher/hangar.png and icon.png generated with built-in image_gen;
exact prompts are in assets/launcher/PROMPTS.txt. Font is OFL Gontserrat from
SDK samples, with license, rendered into an ASCII atlas by tools/make-menu-font.c.
All assets persisted in repo. Shared SDK and ScummVM project untouched.
No source commit/push performed this turn; substantial previous work remains
uncommitted too. No old PS4 installs/packages or game data deleted.

Physical acceptance of the NEW launcher and cross-executable LoadExec remains
pending; 0.05 gameplay acceptance does not prove that new transition on hardware.

## Current: actual engine port (supersedes historical next gates below)

User reports Engine Test 0.04 renders well on physical PS4, but ship controls
do not work. Found two concrete issues: malformed backend GUID has no built-in
GameController mapping, so pilots defaulted to keyboard; backend declares six
axes but emits 0,1,2,4,5,6 (R2 index6 was discarded). Local input.c registers
the actual GUID and wraps SDL_PrivateJoystickAxis to normalize upper slots.
Engine patch0006 enables controller bindings for keyboard-only pilots while
retaining enabled/custom joystick bindings. No remote profiles overwritten.
ASan/UBSan test-input passes all 393216 axis values and mapping registration.
Emulator D1 existing-pilot test logs migration, moves forward, yaws and fires R2;
visually confirmed changed position/orientation, energy99 and projectile impact.
Both engines rebuilt; 0.05 keeps the 0.04 title IDs and external data paths.
Physical input acceptance still pending. User also requests distinct icons OR
a combined package/launcher (prefers the latter); async choice asked, pending.
No new icon or combined launcher implemented yet. Existing runtime icon retained.

Both DXX game engines now cross-compile and link as PS4 executables in
`build/ps4-game/descent1` and `descent2`. Both reached their rendered menu and
pilot-name dialog in shadPS4, visually inspected in `artifacts/dN-ps4-smoke.png`.
This is actual PS4 executable evidence, NOT the earlier Linux host runs.
D1 and D2 additionally reached level 1 with cockpit and textured 3D scene, visually
inspected after test-only Cross/Circle input. HUD/briefing text initially rendered
as solid rectangles: disabling unsupported intensity4/luminance4-alpha4/RGBA2
formats selects RGBA. D1's level screenshot now shows readable HUD text; D2
has been relinked with the same change but not recaptured yet.
Movement/combat, audible sound and physical-console
acceptance remain unverified.

Engine Test 0.04 for both games uploaded to 192.168.32.229:2121 `/data/pkg`:
`Descent-1-PS4-Engine-Test-0.04.pkg` (DSNT00002) and
`Descent-2-PS4-Engine-Test-0.04.pkg` (DSNT00003). Full FTP readback hashes match
the local manifests; PKG validation passes. Neither installed by the agent.
The five pinned demo files were separately uploaded/readback-verified under
`/data/descent-ps4/d1/data` and `d2/data`; no existing files overwritten.
Packages retain the previous runtime-test icon but have distinct Engine Test
titles; no game data inside. Build with `python3 scripts/package-runtime.py
--game 1` (or 2); existing dist files are never overwritten.

Implemented locally, without modifying SDK or sibling projects:

- LLVM 21 C++23 runtime, PhysFS and SDL/PS4GL/native GPU linkage.
- PhysFS native stat ABI conversion: SDK struct uses a 32-bit mode field but
  the kernel uses 16 bits; incorrect size offset truncated the demo HOG.
- HDD-first `/data/descent-ps4/dN/data`, then USB0–7 at
  `/mnt/usbN/descent-ps4/dN/data`; profiles/logs stay on HDD. Fallback order is
  code-reviewed, not yet physically exercised.
- Fixed 1280x720 display, external depth attachment, base-level textures.
- Fan/strip conversion to indexed triangles for the legacy GL client arrays.
  Lines/points remain unsupported by the renderer; automap/crosshair need work.
- U8 game audio conversion to 48kHz S16; not listening-tested. SDL semaphores
  use pthread mutex/condition variables because shadPS4 ksem stubs falsely
  completed thread startup waits, freeing arguments before child consumption.
  Host ASan/UBSan tests pass 100 startup handshakes, timeout and count checks.

Build: `bash scripts/build-ps4-game.sh` completed end-to-end successfully.
Requires sibling ScummVM-PS4 graphics
sources and prebuilt SDL/shader/native libraries (not a standalone release yet).
Capture: `bash scripts/smoke-ps4-game.sh 1` (or 2), sequentially.
Optional `DESCENT_SMOKE_ACCEPT=1` sends seven Cross presses then Circle in isolated Xvfb;
capture is not a pass assertion. Profile lives in `build/emulator-profile`.
Use a single ninja process per output directory. A subsequent dry run still
reports a prematurely ended dependency log and rebuilds all engine objects;
incremental-build bookkeeping needs diagnosis (full build succeeds).
Emulated Cross input advanced D1 from pilot creation to the briefing; the
pilot .plr/.plx were written under the isolated HDD profile. Briefing text has
initially showed solid-color glyph artifacts, corrected in the later D1 HUD
capture by selecting RGBA textures (see above).
At level entry SDL asserted `mouse->WarpMouse`: native PS4 backend has neither
desktop mouse warp nor relative-mode toggle. Engine patch 0005 skips that
desktop toggle on ORBIS (native backend already sends relative mouse deltas).
Both games relinked; D1 and D2 then passed the assertion and rendered level 1.

Remaining gates: level rendering, natural six-axis controller defaults and
menus/save flow, lines/points, sound/music, clean close/relaunch, data-free
package validation and physical PS4 test. Networking compiles because upstream
has unguarded references; it is NOT supported/tested. Random shuffle is disabled.
Current game shutdown reuses tests/ps4-exit.cpp and writes a runtime-probe log
marker: separate this before shipping. Shared renderer C++ libs are older than
the project runtime; startup shader compilation worked, broader ABI unverified.

## Historical runtime diagnostics

Independent checkout and private remote: NichlasEk/Descent-PS4. AvP-PS4 is
unchanged. Runtime-only diagnostic package uploaded to 192.168.32.229:2121:
/data/pkg/Descent-PS4-Runtime-Test-0.01.pkg (7143424 bytes).
SHA-256: 50b07cc6b4a8d9c904a1411d756d38dd54095737d0358865f7eba0a6dcc73fcf.
Package validation and full FTP readback passed. Not installed or launched by
the agent. This is NOT the game and includes no levels. Generated icon explicitly
says RUNTIME TEST. On launch no graphics are rendered; read
/data/descent-ps4/runtime-probe.log for RESULT: PASS. Missing log is not success.

## Verified

- 0.02 physical log reached local destruction, atexit AND fini_array callback,
  then CE-34878-0 was recorded (000001B1.json). The table fix alone did not fix
  the crash. Evidence: artifacts/crash-runtime-002. Remaining boundary was
  stdio cleanup / raw kernel process exit, not the functional C++ checks.
- 0.03 wraps libc's final _exit to request sceSystemServiceLoadExec("exit")
  AFTER normal cleanup. Adjacent Doom3 install-smoke source explicitly notes
  raw _exit caused SIGSYS on hardware; this is supporting evidence, not a
  confirmed Descent exception code. Uses descriptor logging after stdio exit.
- 0.03 package validated and uploaded to /data/pkg with full FTP readback.
  Await installation/start by user; final marker should say libc cleanup
  complete / requesting PS4 system exit. No claim of fixed physical exit yet.

- Physical 0.01 test logged all functional checks PASS, but the console recorded
  CE-34878-0 for DSNT00001. Thus successful process exit was NOT verified.
  Evidence is local in artifacts/crash-runtime-001 (not for publication).
- Exit investigation found missing .fini_array and zero-valued hidden bounds in
  0.01. Added a local supplemental linker script with explicit bounds and a
  diagnostic finalizer. 0.02 has one relocated entry and passes
  tests/test-fini-bounds.py. This is a candidate crash fix, not proven on hardware.
- Runtime-Test-0.02.pkg uploaded alongside 0.01 in /data/pkg, full FTP readback
  verified. Logs now distinguish local cleanup, return from main, atexit and
  fini_array. Ask the user to install/start 0.02, then read the runtime log and
  check whether a fresh application crash was recorded. Normal exit is retained;
  no _Exit workaround. No game package exists yet.

- Pinned DXX-Rebirth source and both PC demos prepared with recorded hashes.
- Both Linux executables build with the local GCC 16 / SDL2 / PhysFS 3.2 stack.
- D1 shareware initially failed at laser03.raw, then corrupt compressed audio.
  The overlay fixes non-NUL basename lookup and an off-by-one compressed-sound
  length index introduced by registering the sound before storing its length.
  Old upstream 0.60.0-beta2 stored the length before incrementing the counter.
- Patched D1 reaches the menu/pilot-name prompt with shareware data, visually
  inspected. D2 demo also reaches its menu/pilot prompt. No gameplay or audible
  sound acceptance yet: host smoke uses dummy audio and disables music.
- Actual patched sound-lookup function passes a mocked hash-boundary test under
  ASan/UBSan, including a non-NUL input and empty/oversized input.
- Current PS4 SDK libc++ is version 11000 and lacks <ranges>. The isolated
  C++23 syntax probe fails there. This has now been bypassed with a separate
  LLVM 21.1.8 runtime build, without changing the installed SDK.
- Project-local libc++, libc++abi and libunwind static libraries build and
  install under build/ps4-deps. The C++23 ranges/span syntax probe passes.
- A PS4-target ELF using locale, stringstream, threads and exceptions links
  successfully: build/ps4-probes/cxx-runtime.elf. Its only dynamic dependency
  is libkernel.so. This is link evidence only: the probe has NOT been run in
  shadPS4 or on hardware. It is now packaged as the runtime-only test above.
- Runtime adaptations route FreeBSD-target/musl locale handling correctly,
  avoid SDK math overload conflicts, and use LLVM's portable timed-backoff
  atomic waits instead of unavailable FreeBSD umtx. Performance untested.

## Commands

```sh
bash scripts/build-linux.sh
python3 tests/test-sound-span.py
bash scripts/smoke-linux.sh d1
bash scripts/smoke-linux.sh d2
bash scripts/build-ps4-runtime.sh
bash scripts/probe-ps4-cxx.sh
bash scripts/link-ps4-runtime-probe.sh
```

Run the smoke tests sequentially: simultaneous xvfb-run -a processes can race
for a display number. Inspect screenshots and logs in artifacts/. Runtime
profiles are isolated with D1X_REBIRTH_HOME/D2X_REBIRTH_HOME under build/profiles,
not the user's normal profile directories. The harness terminates the process
after its capture; this is not a graceful-exit test.

## Next gates

1. Package/run the isolated runtime probe to validate locale, thread and
   exception behavior. Compilation/linking now pass, execution is unverified.
   Do not mix prebuilt C++ renderer dependencies blindly: rebuild against this
   matching runtime or verify ABI compatibility before integration. The legacy
   source baseline remains unselected.
2. Build PS4 PhysFS and select SDL audio/music support; audit the actual OpenGL
   calls against ps4gl before writing adapters.
3. Bring up one D1 level in emulator and then physical PS4. Add D2 after that.
4. Implement/test six-axis controls, HDD-first/USB-fallback data selection and
   fixed HDD saves. These are planned, not currently implemented PS4 features.
5. Keep demos and full retail assets out of Git/public packages until the exact
   distribution boundary has been reviewed.
