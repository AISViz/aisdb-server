import os
from os.path import sep 
import sys
import tarfile
import requests
import subprocess
import shutil


req = requests.get('https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz', stream=True)
tar = f'output{sep}Python-3.9.5.tgz'
with open(tar, 'wb') as f:
    list(map(lambda chunk: f.write(chunk), req.iter_content(chunk_size=1024)))

tarfile.open(tar).extractall(f'output{sep}')
os.chdir(f'output{sep}Python-3.9.5')

subprocess.run('./configure --enable-optimizations --with-lto --disable-ipv6 --enable-loadable-sqlite-extensions'.split())
subprocess.run('make'.split())
subprocess.run('sudo make altinstall'.split())






'''
if not os.path.isdir(f'database{sep}libs'): os.mkdir(f'database{sep}libs')
req = requests.get('http://www.gaia-gis.it/gaia-sins/libspatialite-5.0.1.tar.gz', stream=True)
with open(tar := f'database{sep}libs{sep}libspatialite.tar.tgz', 'wb') as f:
    list(map(lambda chunk: f.write(chunk), req.iter_content(chunk_size=1024)))

tarfile.open(tar).extractall(f'database{sep}libs{sep}')


os.chdir(f'database{sep}libs{sep}libspatialite-5.0.1')

subprocess.run('sudo -E apt-get install libproj-dev')

subprocess.run('./configure --disable-rttopo'.split())
subprocess.run('make')
subprocess.run('sudo -E make install-strip'.split())
'''




import sqlite3
conn = sqlite3.connect(':memory:')
cur = conn.cursor()
conn.enable_load_extension(True)

cur.execute('CREATE VIRTUAL TABLE test USING rtree( id, minMMSI, maxMMSI, minT, maxT, minX, maxX, minY, maxY )')
assert cur.fetchall() == []



#assert conn.execute('SELECT load_extension("mod_spatialite.so")')
#conn.execute('SELECT InitSpatialMetaData(1);') 
