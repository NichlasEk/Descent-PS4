#!/usr/bin/env python3
"""Assemble a relocatable source/relink companion, then test before publication."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain')).resolve()
STACK = ROOT.parent / 'ScummVM-PS4'
BUILD = ROOT / 'build/ps4-game'
out = Path(sys.argv[1]).resolve()
assert (out / 'INVENTORY.json').is_file()
assert not (out / 'BUILD.json').exists(), 'Refusing to reuse assembled companion'
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def copy(source, relative):
    target = out / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return '@KIT@/' + relative
for name in subprocess.check_output(['git', '-C', str(ROOT), 'ls-files'], text=True).splitlines():
    copy(ROOT / name, 'port-source/' + name)
copy(ROOT / 'scripts/companion-build.py', 'build.py')
copy(ROOT / 'docs/SOURCE-COMPANION.md', 'README.md')
for path in (ROOT / 'build/ps4-plan').rglob('*'):
    if path.is_file() and path.suffix in ('.h', '.i'):
        copy(path, 'generated/ps4-plan/' + path.relative_to(ROOT / 'build/ps4-plan').as_posix())
for path in (ROOT / 'build/ps4-deps/include').rglob('*'):
    if path.is_file():
        copy(path, 'generated/runtime-include/' + path.relative_to(ROOT / 'build/ps4-deps/include').as_posix())
for name in ('libc++.a', 'libc++abi.a', 'libunwind.a'):
    copy(ROOT / 'build/ps4-deps/lib' / name, 'libraries/runtime/' + name)
mappings = {
    str(ROOT / 'engine'): '@KIT@/sources/engine',
    str(ROOT / 'build/ps4-plan'): '@KIT@/generated/ps4-plan',
    str(ROOT / 'build/ps4-deps/include'): '@KIT@/generated/runtime-include',
    str(ROOT / 'build/ps4-deps/lib'): '@KIT@/libraries/runtime',
    str(ROOT / 'build/physfs-src'): '@KIT@/sources/physfs',
    str(STACK / 'compat/ps4gl'): '@KIT@/sources/ps4gl',
    str(STACK / '.tools/glslang'): '@KIT@/sources/glslang',
    str(SDK): '@SDK@',
    str(ROOT): '@KIT@/port-source',
}
for name in ('opengnm', 'opengnm-psbc', 'vulkan-ps4', 'Vulkan-Headers', 'SPIRV-Headers'):
    mappings[str(STACK / '.tools/opengnm-stack' / name)] = '@KIT@/sources/' + name
def portable(value):
    value = value.replace(str(ROOT / '../ScummVM-PS4'), str(STACK))
    for before, after in sorted(mappings.items(), key=lambda kv: -len(kv[0])):
        value = value.replace(before, after)
    return value
objects = {}
archives = {}
def capture(path):
    path = path.resolve()
    table, prefix = (objects, 'objects') if path.suffix == '.o' else (archives, 'libraries')
    if str(path) not in table:
        name = f'{prefix}/{len(table):04d}-{digest(path)[:16]}-{path.name}'
        table[str(path)] = copy(path, name)
    return table[str(path)]
provenance = json.loads((ROOT / 'build/ps4-release007/provenance.json').read_text())
links = {}
for target in ('descent1', 'descent2', 'descentlauncher'):
    if target in provenance:
        original = provenance[target]['link_arguments']
        expected = provenance[target]['elf_sha256']
    else:
        line = subprocess.check_output(['ninja', '-C', str(BUILD), '-t', 'commands', target], text=True).splitlines()[-1]
        original = shlex.split(line)[2:-2]
        expected = digest(BUILD / target)
    rewritten = []
    for arg in original:
        # Launcher never references IMG symbols. Relink verification below must
        # prove removing this unused archive changes no executable bytes.
        if target == 'descentlauncher' and arg == str(SDK / 'lib/libSDL2_image.a'):
            continue
        if arg.endswith(('.o', '.a')):
            path = Path(arg) if Path(arg).is_absolute() else BUILD / arg
            arg = portable(str(path)) if path.is_relative_to(SDK) else capture(path)
        else:
            arg = portable(arg)
        rewritten.append(arg)
    rewritten[0] = 'clang++'
    rewritten[rewritten.index('-o') + 1] = '@KIT@/relinked/' + target
    links[target] = dict(arguments=rewritten, expected_elf_sha256=expected)
database = json.loads((ROOT / 'build/ps4-engine/compile_commands.json').read_text())
database += json.loads(subprocess.check_output(['ninja', '-C', str(BUILD), '-t', 'compdb'], text=True))
compilations = []
graphics_objects = []
for entry in database:
    args = entry.get('arguments') or shlex.split(entry.get('command', ''))
    if '-c' not in args or '-o' not in args:
        continue
    original_output = (Path(entry['directory']) / entry['output']).resolve()
    source = (Path(entry['directory']) / entry['file']).resolve()
    if str(original_output) not in objects and not source.is_relative_to(STACK / 'compat/ps4gl'):
        continue
    output = capture(original_output).removeprefix('@KIT@/')
    result = [Path(args[0]).name]
    i = 1
    while i < len(args):
        arg = args[i]
        if arg in ('-MF', '-MT', '-MQ'):
            i += 2
            continue
        if arg in ('-MD', '-MMD'):
            i += 1
            continue
        if arg == '-o':
            result += ['-o', '@KIT@/' + output]
            i += 2
            continue
        result.append(portable(arg))
        i += 1
    compilations.append(dict(object=output, arguments=result))
    if source.is_relative_to(STACK / 'compat/ps4gl'):
        graphics_objects.append(output)
plan = dict(links=links, compilations=compilations, graphics_objects=graphics_objects,
            graphics_archive=archives[str((BUILD / 'libps4_graphics.a').resolve())])
(out / 'BUILD.json').write_text(json.dumps(plan, indent=2) + '\n')
# Full license texts from exact source snapshots, in addition to per-file notices.
notices = {
    'DXX-Rebirth.txt': ROOT / 'engine/COPYING.txt', 'GPL-3.txt': ROOT / 'licenses/GPL-3.txt',
    'PhysFS.txt': ROOT / 'build/physfs-src/LICENSE.txt',
    'SDL.txt': STACK / '.tools/sdl-input-src/COPYING.txt',
    'SDL_image.txt': ROOT / 'build/sdl-image-src/LICENSE.txt',
    'PS4GL-MIT.txt': STACK / 'compat/ps4gl/LICENSE.MIT',
    'glslang.txt': STACK / '.tools/glslang/LICENSE.txt',
    'OpenOrbis.txt': SDK / 'LICENSE',
    'musl.txt': STACK / '.tools/openorbis-musl-2023-reference/COPYRIGHT',
    'MenuFont.txt': ROOT / 'assets/launcher/FONT-LICENSE.txt',
}
for name in ('opengnm', 'opengnm-psbc', 'vulkan-ps4'):
    notices[name + '.txt'] = STACK / '.tools/opengnm-stack' / name / 'LICENSE'
for name in ('libcxx', 'libcxxabi', 'libunwind'):
    notices[name + '.txt'] = ROOT / 'build/llvm-src' / name / 'LICENSE.TXT'
for name, source in notices.items():
    copy(source, 'licenses/' + name)
print(f'{len(compilations)} source compilations, {len(objects)} captured objects; {out}')
