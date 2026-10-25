"""Exact prior bytes for one manually reviewed resource-maintenance batch."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import base64
import json
import resource_followup_history

ROOT = Path(__file__).resolve().parents[1]
BASE = '9c77098763f7f7e43d80a8e6994283484593b78e'
PATHS = {'_source/poker/resources.json', 'downloads/poker-resource-directory.json',
         'downloads/poker-resource-directory.md', 'poker/find/index.html',
         'poker/poker-rules-and-fair-play/index.html', 'poker/resource-quality/index.html',
         'poker/resources/index.html', 'poker/topics/places-to-play/index.html'}
IDS = {'wsop-schedule', 'wpt-schedule', 'ept-schedule', 'apt-schedule', 'pgt',
       'thunder-valley-poker', 'venetian-deepstack', 'mspt-events', 'irish-open-official',
       'appt-official', 'kings-poker-official', 'tda-rule-downloads'}


@lru_cache(maxsize=1)
def change():
    record = json.loads((ROOT / '_tests/resource-review-change.json').read_text(encoding='utf-8'))
    if (type(record.get('version')) is not int or record['version'] != 1
            or record.get('base_commit') != BASE
            or set(record.get('paths', {})) != PATHS
            or set(record.get('resources', {})) != IDS):
        raise ValueError('Unknown resource review predecessor')
    return record


def before(path, data):
    data = resource_followup_history.before(path, data)
    item = change()['paths'].get(str(path))
    if item is None:
        return data
    binary = isinstance(data, bytes)
    raw = data if binary else data.encode('utf-8')
    if sha256(raw).hexdigest() != item['new_sha256']:
        return data
    parts, offset = [], 0
    for start, end, replacement in item['edits']:
        if (type(start) is not int or type(end) is not int
                or not offset <= start <= end <= len(raw)):
            raise ValueError('Invalid resource predecessor offsets: ' + str(path))
        parts.extend((raw[offset:start], base64.b64decode(replacement, validate=True)))
        offset = end
    parts.append(raw[offset:])
    old = b''.join(parts)
    if sha256(old).hexdigest() != item['old_sha256']:
        raise ValueError('Corrupt resource predecessor: ' + str(path))
    return old if binary else old.decode('utf-8')


def resources(records):
    records = resource_followup_history.resources(records)
    pairs = change()['resources']
    return [deepcopy(pairs[r['id']]['old'])
            if r['id'] in pairs and r == pairs[r['id']]['new'] else deepcopy(r)
            for r in records]
