"""Reverse the exact reviewed Turn 08 changes for pinned predecessor tests only.

Unknown versions remain unchanged, exposing unreviewed modifications to older
baseline assertions. Never called by the public site renderer.
"""
from pathlib import Path
from functools import lru_cache
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def change():return json.loads((ROOT/'_tests/time-decision-change.json').read_text())
def before(path,data):
    entry=change().get(str(path))
    if not entry:return data
    binary=isinstance(data,bytes);raw=data if binary else data.encode()
    if sha256(raw).hexdigest()!=entry['new_sha256']:return data
    text=raw.decode()
    for edit in reversed(entry['edits']):
        assert text[edit['start']:edit['end']]==edit['new']
        text=text[:edit['start']]+edit['old']+text[edit['end']:]
    assert sha256(text.encode()).hexdigest()==entry['old_sha256']
    return text.encode() if binary else text
