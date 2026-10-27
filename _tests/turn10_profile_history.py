"""Exact whole-file predecessor view for Turn 10; never rewrite golden baselines."""
import base64,hashlib,json,zlib
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=1)
def records():
    return json.loads((ROOT/'_tests/turn10-profile-change.json').read_text())
def before(path,data):
    # First reverse the later, SHA-pinned public positioning release. This
    # includes the manifest that Turn 10 reads when restoring About/Bio dates.
    import brand_positioning_history as brand_history
    data = brand_history.before(path, data)
    import answer_review_growth_history as guide_growth
    data = guide_growth.before(path, data)
    rec=records().get(str(path))
    if not rec:return data
    binary=isinstance(data,bytes)
    current=data if binary else data.encode('utf-8')
    if hashlib.sha256(current).hexdigest()!=rec['new_sha256']:return data
    original=zlib.decompress(base64.b64decode(rec['old_zlib_b64']))
    if hashlib.sha256(original).hexdigest()!=rec['old_sha256']:
        raise ValueError('Corrupt Turn 10 historical record: '+str(path))
    return original if binary else original.decode('utf-8')


def pages(records):
    """Restore later reviewed metadata before the earlier profile-date boundary."""
    import brand_positioning_history as brand_history
    import answer_review_growth_history as guide_growth
    records = guide_growth.pages(brand_history.pages(records))
    import json as _json
    from copy import deepcopy
    previous = _json.loads(before('_source/pages.json', (ROOT / '_source/pages.json').read_text()))
    dates = {p['id']: p['updated'] for p in previous if p['id'] in {'about', 'bio'}}
    # Older rendered manifests had a separate About update applied by the
    # earlier publication layer. Preserve that pre-Turn-10 metadata boundary.
    dates['about'] = '2026-10-12'
    output = deepcopy(records)
    for p in output:
        if p.get('id') in dates and p.get('updated') == '2026-10-17':
            p['updated'] = dates[p['id']]
    return output
