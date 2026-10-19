"""Test-only exact predecessor of Turn 11 task navigation."""
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
from copy import deepcopy
import base64,zlib,json
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def change():
    data=json.loads((ROOT/'_tests/turn11-task-navigation-change.json').read_text())
    if data['version']!=1 or data['base_commit']!='caa8916ad5738ad53fc39c7df4329a33ed435efa':
        raise ValueError('Unknown navigation release history')
    return data
def before(path,data):
    item=change()['paths'].get(str(path))
    if item is None:return data
    binary=isinstance(data,bytes)
    raw=data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest()!=item['new_sha256']:return data
    restored=zlib.decompress(base64.b64decode(item['old_zlib_base64'],validate=True))
    if sha256(restored).hexdigest()!=item['old_sha256']:
        raise ValueError('Corrupt Turn 11 predecessor: '+str(path))
    return restored if binary else restored.decode('utf-8')
def pages(records):
    changes=change()['pages']
    return [deepcopy(changes[p['id']]['old']) if p['id'] in changes and p==changes[p['id']]['new'] else deepcopy(p) for p in records]
def outputs(records):
    return {p:before(p,v) for p,v in records.items()}
