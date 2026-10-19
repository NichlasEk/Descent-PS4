#!/usr/bin/env python3
"""Regression check: the diagnostic finalizer has a real relocated table."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
elf = root / 'build/ps4-probes/cxx-runtime.elf'
symbols = subprocess.check_output(['readelf', '-sW', str(elf)], text=True)
bounds = {}
for line in symbols.splitlines():
    fields = line.split()
    if fields and fields[-1] in ('__fini_array_start', '__fini_array_end'):
        bounds[fields[-1]] = int(fields[1], 16)
start, end = (bounds[name] for name in ('__fini_array_start', '__fini_array_end'))
assert start > 0 and end - start == 8 and start % 8 == 0, bounds
relocs = subprocess.check_output(['readelf', '-rW', str(elf)], text=True)
assert any(int(fields[0], 16) == start and fields[2] == 'R_X86_64_RELATIVE'
           for line in relocs.splitlines() if len(fields := line.split()) >= 3
           and fields[0].isalnum() and all(c in '0123456789abcdefABCDEF' for c in fields[0]))
print(f'PASS: one relocated finalizer at {start:#x}, end {end:#x}')
