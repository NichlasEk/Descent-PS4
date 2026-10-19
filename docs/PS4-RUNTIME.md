# Isolated PS4 C++ runtime

The pinned DXX engine requires C++23 facilities absent from the installed
OpenOrbis libc++ 11. Build LLVM 21.1.8 locally with:

```sh
bash scripts/build-ps4-runtime.sh
bash scripts/probe-ps4-cxx.sh
bash scripts/link-ps4-runtime-probe.sh
```

The preparation script downloads the official LLVM release archive, verifies
its recorded SHA-256, extracts runtime components and LLVM CMake modules,
and applies runtime-patches idempotently. Hash is locally recorded, not a
publisher signature verification. All generated files remain ignored in build/.
The SDK supplies C headers, libc, startup object and PS4 kernel imports and
is never modified. The runtime retains localization, threads and exceptions;
time-zone database and random-device support are disabled. Filesystem support
is enabled for the renderer dependency, with portable file copying instead of
FreeBSD copy_file_range/sendfile (see runtime patch 0003).

LLVM patches retain upstream licensing (Apache-2.0 WITH LLVM-exception).
Before binary distribution preserve the corresponding LLVM license notices.
Do not relicense the engine or third-party libraries as project-owned code.

## Validation boundary

Both compilation and the standalone runtime probe link pass. No execution of
this runtime on shadPS4 or physical PS4 has been verified. The probe exercises
locale, stringstream, std::thread and throw/catch when eventually run; compiling
it is not evidence that those operations work on the console. Existing renderer
libraries built against old libc++ require an ABI review or matching rebuild.

Toolchain configuration follows the LLVM runtimes standalone build described
in https://libcxx.llvm.org/VendorDocumentation.html.
