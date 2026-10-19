#!/usr/bin/env python3
"""Run in an extracted companion: rebuild port objects and/or relink all games.

The SDK stays external. Source/object paths are relative to this companion.
No shell interpolation; outputs never overwrite the supplied original objects.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--rebuild', action='store_true', help='Compile all engine/platform/PS4GL source objects')
parser.add_argument('--jobs', type=int, default=4)
args = parser.parse_args()
root = Path(__file__).resolve().parent
sdk = Path(os.environ['OO_PS4_TOOLCHAIN']).resolve()
plan = json.loads((root / 'BUILD.json').read_text())
def expand(s):
    return s.replace('@KIT@', str(root)).replace('@SDK@', str(sdk))
out = root / ('rebuilt' if args.rebuild else 'relinked')
out.mkdir(exist_ok=True)
replacements = {}
if args.rebuild:
    def compile_one(entry):
        target = out / entry['object']
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [expand(s) for s in entry['arguments']]
        command[command.index('-o') + 1] = str(target)
        subprocess.run(command, cwd=root, check=True, stdout=subprocess.DEVNULL)
        return expand('@KIT@/' + entry['object']), str(target)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        replacements.update(pool.map(compile_one, plan['compilations']))
    graphics = [replacements[expand('@KIT@/' + name)] for name in plan['graphics_objects']]
    archive = out / 'libps4_graphics.a'
    subprocess.run(['llvm-ar', 'rcs', str(archive), *graphics], check=True)
    replacements[expand(plan['graphics_archive'])] = str(archive)
for name, entry in plan['links'].items():
    command = [replacements.get(expand(s), expand(s)) for s in entry['arguments']]
    command[command.index('-o') + 1] = str(out / name)
    subprocess.run(command, cwd=root, check=True)
    print(out / name, flush=True)
