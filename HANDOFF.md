# Descent PS4 bring-up — 2026-10-19

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
