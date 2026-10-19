#!/usr/bin/env python3
"""Verify packaged payloads and prove the two game SELFs match tested 0.05."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
tool = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain')) / 'bin/linux/PkgTool.Core'
package = root / 'dist/Descent-I-II-PS4-Collection-0.06.pkg'
manifest = json.loads(package.with_suffix('.manifest.json').read_text())
def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()
def extract(path):
    out = Path(tempfile.mkdtemp(prefix='verify-collection-', dir=root / 'build'))
    subprocess.run([str(tool), 'pkg_extract', '--passcode', '0'*32, str(path), str(out)],
                   check=True, stdout=subprocess.DEVNULL)
    return out
assert digest(package) == manifest['sha256'], 'Package hash differs'
out = extract(package)
listing = subprocess.check_output([str(tool), 'pkg_listentries', str(package)], text=True)
indices = {line.split()[-1]: line.split()[3] for line in listing.splitlines() if line.startswith('0x')}
for symbol, filename in [('PARAM_SFO', 'param.sfo'), ('ICON0_PNG', 'icon0.png')]:
    subprocess.run([str(tool), 'pkg_extractentry', str(package), indices[symbol],
                    str(out / 'uroot/sce_sys' / filename)], check=True)
def locate(tree, relative):
    matches = [p for p in tree.rglob(Path(relative).name) if str(p).endswith('/'+relative)]
    assert len(matches) == 1, (relative, matches)
    return matches[0]
for name, expected in manifest['file_sha256'].items():
    if name == 'sce_sys/param.sfo':
        # PkgTool adds publisher tool metadata; verify all authored fields.
        def fields(path):
            lines = subprocess.check_output([str(tool), 'sfo_listentries', str(path)], text=True).splitlines()
            return {line.split(' : ', 1)[0]: line.split(' = ', 1)[1] for line in lines if ' = ' in line and ' : ' in line and not line.startswith('Entry Name')}
        original = fields(Path(manifest['stage']) / name)
        packaged = fields(locate(out, name))
        assert set(packaged) - set(original) == {'PUBTOOLINFO', 'PUBTOOLVER'}
        assert all(packaged[k] == v for k, v in original.items()), 'SFO semantic mismatch'
    else:
        assert digest(locate(out, name)) == expected, name
actual = {p.relative_to(out / 'uroot').as_posix() for p in (out / 'uroot').rglob('*') if p.is_file()}
assert actual == set(manifest['file_sha256']) | {'sce_sys/keystone'}, 'Unexpected payloads'
assert not any(p.suffix.lower() in ('.hog', '.pig', '.ham', '.s22', '.iso') for p in out.rglob('*'))
for game in (1, 2):
    old_pkg = root / f'dist/Descent-{game}-PS4-Engine-Test-0.05.pkg'
    old_manifest = json.loads(old_pkg.with_suffix('.manifest.json').read_text())
    assert digest(old_pkg) == old_manifest['sha256']
    old = extract(old_pkg)
    assert digest(locate(out, f'descent{game}.bin')) == digest(locate(old, 'eboot.bin'))
    print(f'PASS Descent {game}: packaged SELF byte-identical to tested 0.05')
print('PASS payload hashes, authored SFO fields, exact file allowlist and no original game data')
print('Extracted collection:', out)
