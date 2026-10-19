#!/usr/bin/env python3
"""Pin upstream and fetch upstream-recommended demos for local testing only."""
import hashlib
from pathlib import Path
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = '6943b924bea749543ef5729f31a28345e79716d2'
engine = ROOT / 'engine'
if not engine.exists():
    subprocess.run(['git', 'clone', '--no-checkout', 'https://github.com/dxx-rebirth/dxx-rebirth.git', str(engine)], check=True)
    subprocess.run(['git', '-C', str(engine), 'checkout', '--detach', REVISION], check=True)
current = subprocess.check_output(['git', '-C', str(engine), 'rev-parse', 'HEAD'], text=True).strip()
if current != REVISION:
    raise SystemExit(f'Engine revision {current} differs from pin {REVISION}; no checkout changes made')
cache = ROOT / 'build/downloads'
cache.mkdir(parents=True, exist_ok=True)
for game, archive, sha, prefix, names in [
    ('d1', 'desc14sw.tar.gz', '8b65eda01d03401d7a2dc71976528fbb7e0b07a93ce8ee0a9f1d9103623ae249',
     'desc14sw', ['descent.hog', 'descent.pig']),
    ('d2', 'd2shar10.tar.gz', '65e8dc58dc7fdc09696f9a06c814ef81f8026b330976a2dced3347895814a4af',
     'd2shar10', ['d2demo.ham', 'd2demo.hog', 'd2demo.pig']),
]:
    path = cache / archive
    if not path.exists():
        with urllib.request.urlopen('https://icculus.org/d2x/data/' + archive, timeout=60) as stream:
            data = stream.read()
        if hashlib.sha256(data).hexdigest() != sha:
            raise SystemExit('Download checksum mismatch: ' + archive)
        path.write_bytes(data)
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise SystemExit('Cache checksum mismatch: ' + archive)
    dest = ROOT / 'media/demo' / game
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path) as tar:
        for name in names:
            member = tar.getmember(prefix + '/' + name)
            if not member.isfile():
                raise SystemExit('Not a regular data file: ' + name)
            with tar.extractfile(member) as stream:
                data = stream.read()
            target = dest / name
            if target.exists() and target.read_bytes() != data:
                raise SystemExit('Refusing to overwrite different data: ' + str(target))
            if not target.exists():
                target.write_bytes(data)
    print(game, 'demo ready:', dest)
