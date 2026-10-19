#!/usr/bin/env python3
"""Package the diagnostic probe or an explicit game test; never game assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
mode = parser.add_mutually_exclusive_group()
mode.add_argument('--game', type=int, choices=(1, 2))
mode.add_argument('--collection', action='store_true')
args = parser.parse_args()
game, collection = args.game, args.collection
version = '00.06' if collection else '00.05' if game else '00.03'
title_id = 'DSNT00004' if collection else f'DSNT0000{game + 1}' if game else 'DSNT00001'
title = 'Descent I + II' if collection else f'Descent {game} - Engine Test' if game else 'Descent I + II - Runtime Test'
sdk = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain'))
os.environ['OO_PS4_TOOLCHAIN'] = str(sdk)
tool = sdk / 'bin/linux/PkgTool.Core'
stage = Path(tempfile.mkdtemp(prefix='runtime-pkg-', dir=root / 'build'))
dist = root / 'dist'
dist.mkdir(exist_ok=True)
content = f'IV0000-{title_id}_00-DESCENTTEST00001'
assert len(content) == 36
files = []
def run(*args):
    subprocess.run(list(map(str, args)), cwd=stage, check=True)
def copy(source, name):
    target = stage / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    files.append(name)

if not game and not collection:
    run('bash', root / 'scripts/link-ps4-runtime-probe.sh')
elf = root / ('build/ps4-game/descentlauncher' if collection else f'build/ps4-game/descent{game}' if game else 'build/ps4-probes/cxx-runtime.elf')
run(os.environ.get('CREATE_FSELF', '/home/nichlas/ut99-orbis/build/create-fself-current'),
    '-in=' + str(elf),
    '-out=' + str(stage / 'runtime.oelf'), '--eboot', stage / 'eboot.bin',
    '--paid', '0x3800000000000011')
files.append('eboot.bin')
for name in ('sce_sys/about/right.sprx', 'sce_module/libc.prx', 'sce_module/libSceFios2.prx'):
    copy(sdk / 'samples/hello_world' / name, name)
for name in ('libcxx', 'libcxxabi', 'libunwind'):
    copy(root / 'build/llvm-src' / name / 'LICENSE.TXT', 'licenses/' + name + '.txt')
copy(sdk / 'LICENSE', 'licenses/OpenOrbis.txt')
if game or collection:
    copy(root / 'engine/COPYING.txt', 'licenses/DXX-Rebirth.txt')
    copy(root / 'docs/GAME-DATA.txt', 'GAME-DATA.txt')
else:
    copy(root / 'docs/RUNTIME-TEST.txt', 'RUNTIME-TEST.txt')
if collection:
    # Preserve the exact signed game images that were tested on physical PS4.
    for g in (1, 2):
        prior = json.loads((dist / f'Descent-{g}-PS4-Engine-Test-0.05.manifest.json').read_text())
        tested = Path(prior['stage']) / 'eboot.bin'
        if hashlib.sha256((root / f'build/ps4-game/descent{g}').read_bytes()).hexdigest() != prior['elf_sha256']:
            raise SystemExit('Game ELF changed since physical test; refusing silent replacement')
        copy(tested, f'descent{g}.bin')
    copy(root / 'build/launcher-assets/hangar.rgba', 'launcher/hangar.rgba')
    copy(root / 'build/launcher-assets/font.bin', 'launcher/font.bin')
    copy(root / 'assets/launcher/FONT-LICENSE.txt', 'licenses/MenuFont.txt')
icon = root / ('assets/launcher/icon.png' if collection else 'assets/icon-runtime-generated.png')
run('magick', icon, '-resize', '512x512!',
    '-alpha', 'off', '-strip', '-depth', '8', 'PNG24:' + str(stage / 'sce_sys/icon0.png'))
files.append('sce_sys/icon0.png')
sfo = stage / 'sce_sys/param.sfo'
run(tool, 'sfo_new', sfo)
for key, kind, size, value in [
    ('APP_TYPE', 'Integer', 4, '1'), ('APP_VER', 'Utf8', 8, version),
    ('ATTRIBUTE', 'Integer', 4, '0'), ('CATEGORY', 'Utf8', 4, 'gd'),
    ('CONTENT_ID', 'Utf8', 48, content), ('DOWNLOAD_DATA_SIZE', 'Integer', 4, '0'),
    ('SYSTEM_VER', 'Integer', 4, '0'), ('TITLE', 'Utf8', 128, title),
    ('TITLE_ID', 'Utf8', 12, title_id), ('VERSION', 'Utf8', 8, version)]:
    run(tool, 'sfo_setentry', sfo, key, '--type', kind, '--maxsize', size, '--value', value)
files.append('sce_sys/param.sfo')
project = ET.Element('psproject', fmt='gp4', version='1000')
volume = ET.SubElement(project, 'volume')
ET.SubElement(volume, 'volume_type').text = 'pkg_ps4_app'
ET.SubElement(volume, 'volume_id').text = 'PS4VOLUME'
ET.SubElement(volume, 'volume_ts').text = '2026-10-19 00:00:00'
ET.SubElement(volume, 'package', content_id=content, passcode='0'*32,
              storage_type='digital50', app_type='full')
nodes = ET.SubElement(project, 'files', img_no='0')
directories = ET.SubElement(project, 'rootdir')
for name in files:
    ET.SubElement(nodes, 'file', targ_path=name, orig_path=str(stage / name))
    parent = directories
    for part in Path(name).parts[:-1]:
        child = next((x for x in parent if x.get('targ_name') == part), None)
        if child is None:
            child = ET.SubElement(parent, 'dir', targ_name=part)
        parent = child
ET.ElementTree(project).write(stage / 'project.gp4', encoding='utf-8', xml_declaration=True)
run(tool, 'pkg_build', 'project.gp4', stage)
package = dist / ('Descent-I-II-PS4-Collection-0.06.pkg' if collection else f'Descent-{game}-PS4-Engine-Test-0.05.pkg' if game else 'Descent-PS4-Runtime-Test-0.03.pkg')
if package.exists():
    raise SystemExit('Refusing to overwrite existing package: ' + str(package))
shutil.copyfile(stage / (content + '.pkg'), package)
run(tool, 'pkg_validate', package)
with package.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
manifest = dict(package=str(package), sha256=digest, contains_game_data=False,
                runtime_probe_only=not bool(game or collection), game=game, collection=collection, physical_ps4_tested=False,
                elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
                file_sha256={name: hashlib.sha256((stage / name).read_bytes()).hexdigest() for name in files},
                files=files, stage=str(stage))
package.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(package, digest)
