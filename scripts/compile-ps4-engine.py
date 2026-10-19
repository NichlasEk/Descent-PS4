#!/usr/bin/env python3
"""Cross-compile upstream's explicit source plan; never reuse host objects/libs."""
import json
import os
from pathlib import Path
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
sdk = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain'))
plan = root / 'build/ps4-plan'
out = root / 'build/ps4-engine'
out.mkdir(parents=True, exist_ok=True)
entries = json.loads((plan / 'compile_commands.json').read_text())
base = ['clang++', '--target=x86_64-pc-freebsd12-elf', '--sysroot=' + str(sdk),
        '-std=gnu++23', '-fPIC', '-O2', '-g', '-funsigned-char', '-nostdinc++',
        '-D__PS4__', '-D__ORBIS__', '-D_BSD_SOURCE', '-D_GNU_SOURCE',
        '-isystem', str(root / 'build/ps4-deps/include/c++/v1'),
        '-isystem', str(sdk / 'include'), '-isystem', str(sdk / 'include/SDL2'),
        '-I' + str(root / 'platform/ps4'), '-I' + str(root / 'build/physfs-src/src'),
        '-include', str(root / 'platform/ps4/dxxsconf.h')]
rules = ['rule cxx', '  command = $command', '  depfile = $out.d', '  deps = gcc']
database = []
objects = {0: [], 1: [], 2: []}
for entry in entries:
    args = shlex.split(entry['command'])
    if '-c' not in args:
        continue
    output = out / Path(entry['output']).relative_to(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    flags = []
    if '-include' in args:
        index = args.index('-include')
        flags += ['-include', args[index + 1]]
    for arg in args:
        if arg.startswith('-I'):
            path = Path(arg[2:])
            if str(path).startswith('/usr/'):
                continue
            flags.append('-I' + str((Path(entry['directory']) / path).resolve()))
        elif arg.startswith('-D'):
            flags.append(arg)
    source = Path(entry['directory']) / entry['file']
    command = base + flags + ['-MMD', '-MF', str(output) + '.d', '-c', str(source), '-o', str(output)]
    rules += [f'build {output}: cxx {source}', '  command = ' + shlex.join(command).replace('$', '$$')]
    database.append(dict(directory=str(root), file=str(source), output=str(output), arguments=command))
    game = 1 if '-DDXX_BUILD_DESCENT=1' in args else 2 if '-DDXX_BUILD_DESCENT=2' in args else 0
    objects[game].append(str(output))
(out / 'build.ninja').write_text('\n'.join(rules) + '\n')
(out / 'compile_commands.json').write_text(json.dumps(database, indent=2) + '\n')
(out / 'objects.cmake').write_text('\n'.join('set(DESCENT_OBJECTS_' + str(game) + '\n' +
    '\n'.join('  "' + path + '"' for path in paths) + '\n)' for game, paths in objects.items()) + '\n')
subprocess.run(['ninja', '-C', str(out), '-j' + os.environ.get('BUILD_JOBS', '8'), '-k', '12'], check=True)
