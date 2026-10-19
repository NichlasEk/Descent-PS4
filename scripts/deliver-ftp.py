#!/usr/bin/env python3
"""Upload a new private PKG, read it back and verify SHA-256 before publishing it.

Anonymous LAN FTP only. No install, remote overwrite, deletion or credential scan.
"""
import argparse
import ftplib
import hashlib
import json
from pathlib import Path
import uuid

p = argparse.ArgumentParser()
p.add_argument('package', type=Path)
p.add_argument('--host', required=True)
p.add_argument('--port', type=int, default=2121)
p.add_argument('--directory', default='/data/pkg')
a = p.parse_args()
package = a.package.resolve()
manifest = json.loads(package.with_suffix('.manifest.json').read_text())
with package.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
if digest != manifest['sha256']:
    raise SystemExit('Local package does not match its build manifest')
ftp = ftplib.FTP()
ftp.connect(a.host, a.port, timeout=30)
ftp.login()
ftp.cwd(a.directory)
def exists(name):
    return name in [x.rsplit('/', 1)[-1] for x in ftp.nlst()]
if exists(package.name):
    raise SystemExit('Refusing to overwrite existing remote package: '+package.name)
temporary = package.name+'.uploading-'+uuid.uuid4().hex[:12]
print(f'Uploading {package.stat().st_size} bytes to {a.host}:{a.port}{a.directory}/{temporary}', flush=True)
with package.open('rb') as stream:
    ftp.storbinary('STOR '+temporary, stream, blocksize=256*1024)
print('Reading back complete remote upload for SHA-256 verification...', flush=True)
remote = hashlib.sha256()
received = 0
def consume(block):
    global received
    remote.update(block)
    received += len(block)
ftp.retrbinary('RETR '+temporary, consume, blocksize=256*1024)
if received != package.stat().st_size or remote.hexdigest() != digest:
    raise SystemExit('Remote readback mismatch; temporary upload retained: '+temporary)
if exists(package.name):
    raise SystemExit('Remote target appeared during upload; temporary upload retained: '+temporary)
ftp.rename(temporary, package.name)
ftp.quit()
result = dict(host=a.host, port=a.port, remote_path=a.directory+'/'+package.name,
              bytes=received, sha256=digest, full_ftp_readback_verified=True,
              installed=False, physical_ps4_tested=False)
dest = Path(__file__).resolve().parents[1]/'artifacts'/('ftp-'+package.stem+'.json')
dest.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
