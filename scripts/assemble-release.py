#!/usr/bin/env python3
"""Validate and assemble 0.07; does not publish or modify the tested PKG."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '2b71a79f12ebcd7abb1089f556cbd1b82c75f094195ec0ab5ade06f1ea83e2af'
p = argparse.ArgumentParser()
p.add_argument('companion', type=Path)
a = p.parse_args()
kit = a.companion.resolve()
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
package = ROOT / 'dist/Descent-I-II-PS4-Collection-0.07.pkg'
assert digest(package) == EXPECTED, 'Not the physically accepted package'
subprocess.run(['python3', str(ROOT / 'scripts/audit-public-source.py')], check=True)
subprocess.run(['python3', str(ROOT / 'scripts/verify-collection.py'), '--version', '0.07'], check=True)
plan = json.loads((kit / 'BUILD.json').read_text())
for name, entry in plan['links'].items():
    assert digest(kit / 'relinked' / name) == entry['expected_elf_sha256'], name
    rebuilt = kit / 'rebuilt' / name
    assert rebuilt.is_file() and rebuilt.read_bytes()[:4] == b'\x7fELF', name
assert len(plan['compilations']) == 242
assert len({c['object'] for c in plan['compilations']}) == 242
inventory = json.loads((kit / 'INVENTORY.json').read_text())
files = set()
for label, record in inventory['sources'].items():
    for name, expected in record['files'].items():
        relative = 'sources/' + label + '/' + name
        assert digest(kit / relative) == expected, 'Snapshot changed: ' + relative
        files.add(relative)
# Refresh only the known port-source files after release documentation is final.
for name in subprocess.check_output(['git', '-C', str(ROOT), 'ls-files'], text=True).splitlines():
    target = kit / 'port-source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
for directory in ('port-source', 'licenses', 'objects', 'libraries', 'generated', 'build-reference'):
    files.update(path.relative_to(kit).as_posix() for path in (kit / directory).rglob('*') if path.is_file())
files.update(('BUILD.json', 'build.py', 'README.md'))
spec = importlib.util.spec_from_file_location('source_audit', ROOT / 'scripts/audit-public-source.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
for name in sorted(files):
    path = kit / name
    assert not path.is_symlink() and '..' not in Path(name).parts
    if not name.startswith(('objects/', 'libraries/')):
        audit.check(name, path.read_bytes())
inventory['public_release_ready'] = True
inventory['blockers'] = []
inventory['validation'] = {
    'physical_007_accepted_by_maintainer': True,
    'byte_identical_relinks': list(plan['links']),
    'engine_platform_renderer_source_objects_rebuilt': len(plan['compilations']),
    'full_sdk_reproducibility_claimed': False,
}
(kit / 'INVENTORY.json').write_text(json.dumps(inventory, indent=2) + '\n')
files.add('INVENTORY.json')
manifest = {name: digest(kit / name) for name in sorted(files)}
(kit / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
files.add('MANIFEST.json')
dest = ROOT / 'dist/release-v0.07'
dest.mkdir(exist_ok=False)
archive = dest / 'Descent-PS4-v0.07-source-relink.tar.gz'
with tarfile.open(archive, 'w:gz') as tar:
    for name in sorted(files):
        path = kit / name
        info = tar.gettarinfo(str(path), arcname='Descent-PS4-source/' + name)
        info.uid = info.gid = info.mtime = 0
        info.uname = info.gname = ''
        with path.open('rb') as stream:
            tar.addfile(info, stream)
with tarfile.open(archive) as tar:
    seen = set()
    for member in tar:
        name = member.name.removeprefix('Descent-PS4-source/')
        assert member.isfile() and name in files and name not in seen
        seen.add(name)
        with tar.extractfile(member) as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == digest(kit / name), name
    assert seen == files
bundle = dest / 'Descent-I-II-PS4-v0.07.zip'
entries = {package.name: package, 'GAME-DATA.txt': ROOT / 'docs/GAME-DATA.txt',
           'README.md': ROOT / 'README.md', 'LICENSE': ROOT / 'LICENSE',
           'THIRD-PARTY.md': ROOT / 'docs/THIRD-PARTY.md', 'RELEASE.md': ROOT / 'docs/RELEASE.md'}
entries.update({'licenses/' + path.name: path for path in (kit / 'licenses').iterdir() if path.is_file()})
with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for name, path in entries.items():
        z.write(path, name)
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == set(entries)
    for name, path in entries.items():
        with z.open(name) as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == digest(path)
shutil.copyfile(ROOT / 'docs/GAME-DATA.txt', dest / 'GAME-DATA.txt')
(dest / 'SHA256SUMS').write_text(''.join(f'{digest(path)}  {path.name}\n'
    for path in sorted(dest.iterdir()) if path.is_file()))
print(f'PASS {len(files)} companion files and distribution ZIP read back; {dest}')
