"""Reverse only the frozen search-section addition; retain all old golden hashes."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def change():return json.loads((ROOT/'_tests/search-sections-change.json').read_text())

def before(path,data):
    path=str(path);c=change()
    if path not in set(c['patches'])|{'find/index.html'}:return data
    binary=isinstance(data,bytes);text=data.decode() if binary else data
    if path=='find/index.html':
        block=re.search(r'<!-- Search section index: start -->.*?<!-- Search section index: end -->\n',text,re.S)
        if block and sha256(block[0].encode()).hexdigest()==c['block_sha256']:
            text=text.replace(block[0],'',1)
        for asset,(old,new) in c['versions'].items():
            text=text.replace('/'+asset+'?v='+new[:12],'/'+asset+'?v='+old[:12],1)
    source='_source/find.html' if path=='find/index.html' else path
    for old,new in reversed(c['patches'].get(source,[])):
        text=text.replace(new,old,1)
    return text.encode() if binary else text
