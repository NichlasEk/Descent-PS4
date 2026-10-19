#!/usr/bin/env python3
"""Relink the tested objects with pinned SDL_image; preserve every old ELF/PKG."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / 'build/ps4-game'
out = root / 'build/ps4-release007'
out.mkdir(exist_ok=False)
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
records = {}
for game in (1, 2):
    target = f'descent{game}'
    old = json.loads((root / f'dist/Descent-{game}-PS4-Engine-Test-0.05.manifest.json').read_text())
    assert digest(build / target) == old['elf_sha256'], 'Original tested ELF changed'
    # -t commands does not regenerate or build the old Ninja plan.
    lines = subprocess.check_output(['ninja', '-C', str(build), '-t', 'commands', target], text=True).splitlines()
    args = shlex.split(lines[-1])
    assert args[:2] == [':', '&&'] and args[-2:] == ['&&', ':']
    args = args[2:-2]
    old_image = [a for a in args if a.endswith('/lib/libSDL2_image.a')]
    assert len(old_image) == 1, 'Expected old SDK image archive in original link plan'
    args[args.index(old_image[0])] = str(root / 'build/ps4-image/libSDL2_image.a')
    index = args.index('-o') + 1
    assert args[index] == target
    args[index] = str(out / target)
    inputs = {}
    for arg in args:
        if arg.endswith(('.o', '.a')):
            path = Path(arg) if Path(arg).is_absolute() else build / arg
            inputs[str(path.relative_to(root)) if path.is_relative_to(root) else str(path)] = digest(path)
    subprocess.run(args, cwd=build, check=True)
    records[target] = dict(original_elf_sha256=old['elf_sha256'],
                           elf_sha256=digest(out / target), link_inputs=inputs,
                           link_arguments=args)
(out / 'provenance.json').write_text(json.dumps(records, indent=2) + '\n')
print(out)
