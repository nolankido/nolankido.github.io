"""Restore only the exact previous identity export for historical tests.

Turn 3 removes a stale home-location assertion. Older release contracts must
still see their original reviewed input, not silently rewrite the evidence.
This module is test-only; the site build never imports it.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = '18a9c8ca15682752cd59d83ba9c79b6d4f564526'
REVISIONS = {
    '_source/person-schema.jsonld': (
        '0865b0fb0d7691429b51d17b748e87bbb398bdbb8c8d442c99cea9047f918360',
        'ce987629042809fb9060acffa1e795b83ad4918692d7ff2540ac9e00eb713abd',
    ),
    'assets/nolan-kido-identity.jsonld': (
        '721e0658e3caccd81b17882c041ff6693681670c59e7265c971f9819fa0546fc',
        '55f464baafdc1c5259e2dd92aa74e4b9ee019d74696f316d8d78f0acf4411e27',
    ),
}
OLD_SUFFIX = 'Tournament poker player. Honolulu, Hawaiʻi.'
NEW_SUFFIX = 'Tournament poker player.'
VERIFIED_PROFILE_ADDITION = '        "https://dev.to/kidon",\n'
ALUMNI_START = '      "alumniOf": {\n'
PREVIOUS_LOCATION = (
    '      "homeLocation": {\n'
    '        "@type": "Place",\n'
    '        "address": {\n'
    '          "@type": "PostalAddress",\n'
    '          "addressLocality": "Honolulu",\n'
    '          "addressRegion": "HI",\n'
    '          "addressCountry": "US"\n'
    '        }\n'
    '      },\n'
)


def digest(value: str | bytes) -> str:
    return sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def key(path: str | Path) -> str:
    target = Path(path)
    if target.is_absolute():
        try:
            target = target.relative_to(ROOT)
        except ValueError:
            return target.as_posix()
    return target.as_posix()


def before(path: str | Path, data: str | bytes) -> str | bytes:
    """Recreate the prior bytes only from an exact, reviewed successor hash."""
    hashes = REVISIONS.get(key(path))
    if hashes is None or digest(data) != hashes[1]:
        return data
    text = data.decode('utf-8') if isinstance(data, bytes) else data
    if text.count(NEW_SUFFIX) != 1 or text.count(ALUMNI_START) != 1:
        raise ValueError('Invalid identity Turn 3 successor boundary')
    if text.count(VERIFIED_PROFILE_ADDITION) != 1:
        raise ValueError('Invalid identity Turn 3 verified-profile boundary')
    old = (text.replace(VERIFIED_PROFILE_ADDITION, '', 1)
           .replace(NEW_SUFFIX, OLD_SUFFIX, 1)
           .replace(ALUMNI_START, PREVIOUS_LOCATION + ALUMNI_START, 1))
    if digest(old) != hashes[0]:
        raise ValueError('Invalid identity Turn 3 predecessor digest')
    return old.encode('utf-8') if isinstance(data, bytes) else old
