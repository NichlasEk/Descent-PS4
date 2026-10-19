# Descent PS4 bring-up — 2026-10-19

Independent checkout and private remote: NichlasEk/Descent-PS4. AvP-PS4 is
unchanged. Nothing uploaded to the console; no PS4 package exists yet.

## Verified

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
  C++23 syntax probe fails there. This is a confirmed cross-build prerequisite,
  not a graphics or physical-console failure.

## Commands

```sh
bash scripts/build-linux.sh
python3 tests/test-sound-span.py
bash scripts/smoke-linux.sh d1
bash scripts/smoke-linux.sh d2
bash scripts/probe-ps4-cxx.sh # expected to fail with the installed old SDK
```

Run the smoke tests sequentially: simultaneous xvfb-run -a processes can race
for a display number. Inspect screenshots and logs in artifacts/. Runtime
profiles are isolated with D1X_REBIRTH_HOME/D2X_REBIRTH_HOME under build/profiles,
not the user's normal profile directories. The harness terminates the process
after its capture; this is not a graceful-exit test.

## Next gates

1. Resolve modern C++ library support in an isolated PS4 dependency build,
   without replacing the working SDK used by AvP. A legacy source baseline is
   an alternative to investigate, not selected: 0.60.0-beta2 was inspected only.
2. Build PS4 PhysFS and select SDL audio/music support; audit the actual OpenGL
   calls against ps4gl before writing adapters.
3. Bring up one D1 level in emulator and then physical PS4. Add D2 after that.
4. Implement/test six-axis controls, HDD-first/USB-fallback data selection and
   fixed HDD saves. These are planned, not currently implemented PS4 features.
5. Keep demos and full retail assets out of Git/public packages until the exact
   distribution boundary has been reviewed.
