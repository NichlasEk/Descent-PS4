#!/usr/bin/env python3
"""Snapshot local corresponding-source candidates, without publishing anything.

Deliberately fails the public-release gate while provenance gaps remain. A source
inventory is not proof of binary/source identity or a reproducible build.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT.parent / 'ScummVM-PS4'
SDK = Path(os.environ.get('OO_PS4_TOOLCHAIN', '/opt/openorbis/OpenOrbis/PS4Toolchain'))
NATIVE = STACK / '.tools/opengnm-stack'

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    out = Path(tempfile.mkdtemp(prefix='release-sources-', dir=ROOT / 'build'))
    records = {}
    skipped = []
    roots = {
        'engine': ROOT / 'engine',
        'physfs': ROOT / 'build/physfs-src',
        'ps4gl': STACK / 'compat/ps4gl',
        'sdl': STACK / '.tools/sdl-input-src',
        'sdl-image': ROOT / 'build/sdl-image-src',
        'glslang': STACK / '.tools/glslang',
        'opengnm': NATIVE / 'opengnm',
        'vulkan-ps4': NATIVE / 'vulkan-ps4',
        'opengnm-psbc': NATIVE / 'opengnm-psbc',
        'Vulkan-Headers': NATIVE / 'Vulkan-Headers',
        'SPIRV-Headers': NATIVE / 'SPIRV-Headers',
        'openorbis-modules': SDK / 'src/modules',
        'openorbis-crt': SDK / 'src/crt',
    }
    roots['sdk-musl-reference'] = STACK / '.tools/openorbis-musl-2023-reference'
    roots['sdk-compiler-rt-reference'] = STACK / '.tools/openorbis-llvm-v12-reference/compiler-rt'
    for name in ('libc', 'libcxx', 'libcxxabi', 'libunwind', 'cmake', 'runtimes', 'llvm'):
        roots['llvm21/' + name] = ROOT / 'build/llvm-src' / name
    suffixes = {'.c', '.h', '.cc', '.cpp', '.hpp', '.inc', '.inl', '.S', '.s',
                '.cmake', '.mak', '.mk', '.py', '.sh', '.bat', '.txt', '.md', '.rst',
                '.in', '.y', '.l', '.json', '.xml', '.yaml', '.yml', '.def', '.td',
                '.cl', '.map', '.lds', '.x', '.mako', '.rnc', '.rng', '.gn', '.gni',
                '.m4', '.am', '.ac', '.spec', '.patch', '.diff', '.tbl'}
    ignored = {'.git', '__pycache__', 'build', 'out', 'node_modules', '.cache'}
    forbidden = {'.iso', '.pkg', '.hog', '.pig', '.ham', '.s11', '.s22', '.prx',
                 '.sprx', '.elf', '.oelf', '.exe', '.a', '.o', '.so', '.dll', '.bin'}
    def copy(source, name):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return digest(target)
    for label, directory in roots.items():
        if not directory.is_dir():
            raise SystemExit('Missing source root: ' + str(directory))
        record = {'files': {}}
        if (directory / '.git').exists():
            record['revision'] = subprocess.check_output(
                ['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
            record['changes'] = subprocess.check_output(
                ['git', '-C', str(directory), 'diff', '--stat'], text=True)
        for path in sorted(directory.rglob('*')):
            rel = path.relative_to(directory)
            if not path.is_file() or path.is_symlink() or any(p in ignored for p in rel.parts):
                continue
            if path.suffix.lower() in forbidden:
                continue
            # Preserve ALL text inputs, including .tcc, shader fixtures, codegen
            # CSV files and configure files. An extension allowlist lost sources.
            # Exclude extensionless compiled tools; preserve text build scripts.
            with path.open('rb') as stream:
                head = stream.read()
            if b'\0' in head or head.startswith((b'\x7fELF', b'MZ')):
                skipped.append(label + '/' + rel.as_posix())
                continue
            record['files'][rel.as_posix()] = copy(path, 'sources/' + label + '/' + rel.as_posix())
        records[label] = record
    for name in ('build-ps4-input.sh', 'build-ps4-sdlgl.sh', 'build-ps4-glslang.sh',
                 'build-opengnm-probe.sh', 'prepare-opengnm-psbc.py',
                 'psbc-codegen-requirements.txt', 'build-scummvm-vulkan.sh'):
        copy(STACK / 'scripts' / name, 'build-reference/' + name)
    for path in sorted((STACK / 'patches/opengnm').glob('*.patch')):
        copy(path, 'build-reference/patches/' + path.name)
    modules = {}
    for packaged, built in [('sce_module/libc.prx', 'libc/libc.prx'),
                            ('sce_module/libSceFios2.prx', 'libSceFios2/libSceFios2.prx'),
                            ('sce_sys/about/right.sprx', 'right/right.sprx')]:
        actual = digest(SDK / 'samples/hello_world' / packaged)
        if actual != digest(SDK / 'src/modules' / built):
            raise SystemExit('SDK module/source-build mismatch: ' + packaged)
        modules[packaged] = actual
    report = {
        'public_release_ready': False,
        'blockers': [
            '0.07 physically accepted by maintainer; assembly checks are separate.',
            'Source snapshots and build references still need a complete clean-build integration check.',
        ],
        'sdk_module_identity': modules,
        'sources': records,
        'skipped_non_source_candidates': skipped,
    }
    (out / 'INVENTORY.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out)
    print('PRIVATE preparation only: public_release_ready=false')

if __name__ == '__main__':
    main()
