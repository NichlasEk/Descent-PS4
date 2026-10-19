#!/usr/bin/env python3
"""Prepare a pinned, project-local LLVM runtime source tree (never modify SDK)."""
import hashlib
from pathlib import Path
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
VERSION = "21.1.8"
NAME = f"llvm-project-{VERSION}.src.tar.xz"
SHA256 = "4633a23617fa31a3ea51242586ea7fb1da7140e426bd62fc164261fe036aa142"
archive = ROOT / "build/downloads" / NAME
source = ROOT / "build/llvm-src"
archive.parent.mkdir(parents=True, exist_ok=True)
if not archive.exists():
    temporary = archive.with_suffix(".partial")
    urllib.request.urlretrieve(
        f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{VERSION}/{NAME}",
        temporary,
    )
    temporary.rename(archive)
with archive.open("rb") as stream:
    if hashlib.file_digest(stream, "sha256").hexdigest() != SHA256:
        raise SystemExit(f"Hash mismatch: {archive}; refusing extraction")
source.mkdir(parents=True, exist_ok=True)
components = {"cmake", "runtimes", "libc", "libcxx", "libcxxabi", "libunwind", "llvm"}
missing = {name for name in components if not (source / name).exists()}
if missing:
    with tarfile.open(archive) as tar:
        for member in tar:
            parts = Path(member.name).parts
            if len(parts) < 2 or parts[1] not in missing:
                continue
            if parts[1] == "llvm" and len(parts) > 2 and parts[2] != "cmake":
                continue
            member.name = str(Path(*parts[1:]))
            tar.extract(member, source, filter="data")
for patch in sorted((ROOT / "runtime-patches").glob("*.patch")):
    command = ["patch", "--batch", "-p1", "-i", str(patch)]
    applied = subprocess.run(command + ["--dry-run", "--reverse"], cwd=source,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if applied.returncode:
        subprocess.run(command + ["--dry-run", "--forward"], cwd=source, check=True)
        subprocess.run(command + ["--forward"], cwd=source, check=True)
print(f"LLVM {VERSION} runtime sources ready: {source}")
