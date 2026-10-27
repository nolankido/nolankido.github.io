"""Exact test-only boundary for the identity and positioning publications.

Old release assertions must compare old release inventories, not the current
site. Only complete reviewed files can be removed or rewound here. Unrecognized
additions and mutations remain visible. The live build never imports this file.
"""
from hashlib import sha256
from pathlib import Path

import brand_positioning_history

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PARENT = '9787706ef4409606d37ed73202016b506b99d1eb'
IDENTITY_RELEASE = '59781671d4b2722186195a9d3315da30add8ae6f'
IDENTITY_TREE = 'bf4c55a99ba20ef463f2564bc356412649d55062'
IDENTITY_BUILD = '_scripts/build.py'
BUILD_BEFORE = 'b24500bb8d095eaaa46262817290aa5229ac2d48efbb0e62cce6d29006314f59'
BUILD_AFTER = 'ec6b62e3dcc56fbabcd1a32d2fe846fd071e6c4cfb55bd365da65f5fb2375178'
BUILD_INSERTION = (
    "    identity_document = json.loads((SOURCE / 'person-schema.jsonld').read_text(encoding='utf-8'))\n"
    "    outputs[Path('assets/nolan-kido-identity.jsonld')] = json.dumps(identity_document, ensure_ascii=False, indent=2) + '\\n'\n"
)
OUTPUT_ADDITIONS = {
    'assets/nolan-kido-identity.jsonld':
        '721e0658e3caccd81b17882c041ff6693681670c59e7265c971f9819fa0546fc',
}
SOURCE_ADDITIONS = {
    **OUTPUT_ADDITIONS,
    '_source/person-schema.jsonld':
        '0865b0fb0d7691429b51d17b748e87bbb398bdbb8c8d442c99cea9047f918360',
    'assets/social/nolan-kido-ai.png':
        '646c36e15b25af45e21d372a6daf2641e5d8cd11fb460411dcf8d21938558877',
}
LIVE_TARGET_ADDITIONS = {
    '/assets/social/nolan-kido-ai.png': SOURCE_ADDITIONS['assets/social/nolan-kido-ai.png'],
}
# These author test fixtures, not published pages or runtime assets. Their own
# tests check behavior; old production inventories predate these exact tools.
TEST_UTILITIES = frozenset({
    '_scripts/freeze_brand_positioning_delta.py',
    '_scripts/freeze_scoped_share_change.py',
})


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def digest(data):
    return sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


def before(path, data):
    name = key(path)
    data = brand_positioning_history.before(name, data)
    if name != IDENTITY_BUILD or digest(data) != BUILD_AFTER:
        return data
    binary = isinstance(data, bytes)
    text = data.decode('utf-8') if binary else data
    if text.count(BUILD_INSERTION) != 1:
        raise ValueError('Invalid standalone identity build insertion')
    previous = text.replace(BUILD_INSERTION, '', 1)
    if digest(previous) != BUILD_BEFORE:
        raise ValueError('Invalid standalone identity build predecessor')
    return previous.encode('utf-8') if binary else previous


def pages(records):
    return brand_positioning_history.pages(records)


def _keep(path, data, additions):
    expected = additions.get(key(path))
    return expected is None or digest(data) != expected


def outputs(records):
    """Rewind generated outputs, dropping only the exact added JSON-LD asset."""
    return {path: before(path, value) for path, value in records.items()
            if _keep(path, value, OUTPUT_ADDITIONS)}


def source_records(records):
    """Rewind source/asset inventories without hiding altered additions."""
    return {path: before(path, value) for path, value in records.items()
            if key(path) not in TEST_UTILITIES and _keep(path, value, SOURCE_ADDITIONS)}


def files(paths):
    """Preserve input path types and only exclude known, exact later additions."""
    def keep(path):
        name = key(path)
        if name in TEST_UTILITIES:
            return False
        if name not in SOURCE_ADDITIONS:
            return True
        return _keep(name, (ROOT / path).read_bytes(), SOURCE_ADDITIONS)
    return type(paths)(path for path in paths if keep(path))


def live_targets(records):
    """Restore the old target count without dropping an unrecognized response."""
    def keep(route, response):
        expected = LIVE_TARGET_ADDITIONS.get(route)
        if (expected is None or not isinstance(response, tuple) or len(response) != 2
                or type(response[0]) is not int or response[0] != 200
                or not isinstance(response[1], bytes)):
            return True
        return digest(response[1]) != expected
    return {route: response for route, response in records.items() if keep(route, response)}
