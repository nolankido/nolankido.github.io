"""Exact reviewed predecessor, guarded by complete digests and record equality."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import holdem_essay_history as essay
import turn09_weekly_reset_history as weekly_history
ROOT=Path(__file__).resolve().parents[1]
OUTPUT='living-well/ai-and-personal-productivity/index.html'
@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT/'_tests/productivity-change.json').read_text())
def before(path,data):
    data=essay.before(path,data)
    entry=change()['paths'].get(str(path));binary=isinstance(data,bytes);raw=data if binary else data.encode()
    if not entry or sha256(raw).hexdigest()!=entry['new_sha256']:return data
    text=raw.decode()
    for edit in reversed(entry['edits']):
        assert text[edit['start']:edit['end']]==edit['new']
        text=text[:edit['start']]+edit['old']+text[edit['end']:]
    assert sha256(text.encode()).hexdigest()==entry['old_sha256']
    return text.encode() if binary else text
def restore(records,field,key,new):
    c=change();result=[]
    for r in records:
        if r==c[new]:continue
        pair=c[field].get(r[key]);result.append(deepcopy(pair['old']) if pair and r==pair['new'] else deepcopy(r))
    return result
def pages(records):return restore(essay.pages(records),'pages','id','page')
def entries(records):return restore([weekly_history.original_entry(r) for r in records],'entries','slug','entry')
def outputs(records):
    return {p:before(p,v) for p,v in essay.outputs(records).items() if change()['new_outputs'].get(str(p))!=sha256(v.encode()).hexdigest()}
def files(paths):
    def original(path):
        key=Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else str(path)
        return change()['new_files'].get(key)!=sha256((ROOT/path).read_bytes()).hexdigest()
    return type(paths)(p for p in essay.files(paths) if original(p))
