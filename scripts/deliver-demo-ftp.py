#!/usr/bin/env python3
"""Deliver pinned local demos separately from PKGs, without overwriting files."""
import ftplib
import hashlib
from pathlib import Path
import uuid

root = Path(__file__).resolve().parents[1]
ftp = ftplib.FTP()
ftp.connect('192.168.32.229', 2121, timeout=30)
ftp.login()
ftp.cwd('/data/descent-ps4')
def enter(name):
    if name not in ftp.nlst():
        ftp.mkd(name)
    ftp.cwd(name)
def remote_hash(name):
    digest = hashlib.sha256()
    ftp.retrbinary('RETR ' + name, digest.update, blocksize=256*1024)
    return digest.hexdigest()
for game, names in [(1, ('descent.hog', 'descent.pig')),
                    (2, ('d2demo.hog', 'd2demo.ham', 'd2demo.pig'))]:
    ftp.cwd('/data/descent-ps4')
    enter(f'd{game}')
    enter('data')
    for name in names:
        local = root / f'media/demo/d{game}' / name
        with local.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        if name in ftp.nlst():
            if remote_hash(name) != digest:
                raise SystemExit('Refusing to replace different remote data: ' + name)
            print('Verified existing', game, name, flush=True)
            continue
        temp = name + '.uploading-' + uuid.uuid4().hex[:12]
        with local.open('rb') as source:
            ftp.storbinary('STOR ' + temp, source, blocksize=256*1024)
        if remote_hash(temp) != digest:
            raise SystemExit('Readback mismatch: ' + temp)
        if name in ftp.nlst():
            raise SystemExit('Target appeared during upload: ' + name)
        ftp.rename(temp, name)
        print('Delivered and readback verified', game, name, digest, flush=True)
ftp.quit()
