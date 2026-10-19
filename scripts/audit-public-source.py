#!/usr/bin/env python3
"""Check current publishable files and reachable Git blobs; print no secrets.

This is a bounded signature/file-type audit, not a guarantee of secret absence.
Ignored local game/build data is never added or read by the working-tree audit.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DENIED = {'.iso', '.pkg', '.hog', '.pig', '.ham', '.s11', '.s22', '.prx', '.sprx',
          '.elf', '.oelf', '.exe', '.o', '.a', '.rif', '.pfx', '.p12'}
SECRETS = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
           rb'gh[pousr]_[A-Za-z0-9]{36,}', rb'github_pat_[A-Za-z0-9_]{60,}',
           rb'AKIA[A-Z0-9]{16}']

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def check(name, data):
    if Path(name).suffix.lower() in DENIED:
        raise SystemExit('Forbidden public file type: ' + name)
    if data.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')):
        raise SystemExit('Unexpected executable/archive: ' + name)
    if any(re.search(pattern, data) for pattern in SECRETS):
        raise SystemExit('Potential secret signature in: ' + name)

def main():
    names = set(git('ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')) - {b''}
    for encoded in names:
        name = encoded.decode()
        path = ROOT / name
        if path.is_symlink():
            raise SystemExit('Review symlink before publication: ' + name)
        if path.is_file():
            check(name, path.read_bytes())
    blobs = 0
    for line in git('rev-list', '--objects', '--all').decode().splitlines():
        fields = line.split(' ', 1)
        if len(fields) != 2:
            continue
        oid, name = fields
        if git('cat-file', '-t', oid).strip() != b'blob':
            continue
        check(name, git('cat-file', 'blob', oid))
        blobs += 1
    print(f'PASS: {len(names)} current files and {blobs} historical blobs; bounded signature/type audit')

if __name__ == '__main__':
    main()
