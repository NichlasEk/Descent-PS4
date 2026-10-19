#!/usr/bin/env python3
"""Package only the diagnostic runtime probe; never include game assets."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
sdk = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain'))
os.environ['OO_PS4_TOOLCHAIN'] = str(sdk)
tool = sdk / 'bin/linux/PkgTool.Core'
stage = Path(tempfile.mkdtemp(prefix='runtime-pkg-', dir=root / 'build'))
dist = root / 'dist'
dist.mkdir(exist_ok=True)
content = 'IV0000-DSNT00001_00-DESCENTTEST00001'
assert len(content) == 36
files = []
def run(*args):
    subprocess.run(list(map(str, args)), cwd=stage, check=True)
def copy(source, name):
    target = stage / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    files.append(name)

run('bash', root / 'scripts/link-ps4-runtime-probe.sh')
run(os.environ.get('CREATE_FSELF', '/home/nichlas/ut99-orbis/build/create-fself-current'),
    '-in=' + str(root / 'build/ps4-probes/cxx-runtime.elf'),
    '-out=' + str(stage / 'runtime.oelf'), '--eboot', stage / 'eboot.bin',
    '--paid', '0x3800000000000011')
files.append('eboot.bin')
for name in ('sce_sys/about/right.sprx', 'sce_module/libc.prx', 'sce_module/libSceFios2.prx'):
    copy(sdk / 'samples/hello_world' / name, name)
for name in ('libcxx', 'libcxxabi', 'libunwind'):
    copy(root / 'build/llvm-src' / name / 'LICENSE.TXT', 'licenses/' + name + '.txt')
copy(sdk / 'LICENSE', 'licenses/OpenOrbis.txt')
copy(root / 'docs/RUNTIME-TEST.txt', 'RUNTIME-TEST.txt')
run('magick', root / 'assets/icon-runtime-generated.png', '-resize', '512x512!',
    '-alpha', 'off', '-strip', '-depth', '8', 'PNG24:' + str(stage / 'sce_sys/icon0.png'))
files.append('sce_sys/icon0.png')
sfo = stage / 'sce_sys/param.sfo'
run(tool, 'sfo_new', sfo)
for key, kind, size, value in [
    ('APP_TYPE', 'Integer', 4, '1'), ('APP_VER', 'Utf8', 8, '00.01'),
    ('ATTRIBUTE', 'Integer', 4, '0'), ('CATEGORY', 'Utf8', 4, 'gd'),
    ('CONTENT_ID', 'Utf8', 48, content), ('DOWNLOAD_DATA_SIZE', 'Integer', 4, '0'),
    ('SYSTEM_VER', 'Integer', 4, '0'), ('TITLE', 'Utf8', 128, 'Descent I + II - Runtime Test'),
    ('TITLE_ID', 'Utf8', 12, 'DSNT00001'), ('VERSION', 'Utf8', 8, '00.01')]:
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
package = dist / 'Descent-PS4-Runtime-Test-0.01.pkg'
if package.exists():
    raise SystemExit('Refusing to overwrite existing package: ' + str(package))
shutil.copyfile(stage / (content + '.pkg'), package)
run(tool, 'pkg_validate', package)
with package.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
manifest = dict(package=str(package), sha256=digest, contains_game_data=False,
                runtime_probe_only=True, physical_ps4_tested=False, files=files, stage=str(stage))
package.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(package, digest)
