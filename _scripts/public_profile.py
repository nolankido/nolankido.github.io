"""Reusable introductions come from the existing public identity, not new claims."""
from pathlib import Path

EXPORTS = {
    'bio_short': Path('downloads/nolan-kido-short-bio.txt'),
    'bio_long': Path('downloads/nolan-kido-long-bio.txt'),
}


def exports(site: dict) -> dict[Path, str]:
    result = {}
    for key, path in EXPORTS.items():
        value = site.get(key)
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError('A public biography must be a nonempty, trimmed string: ' + key)
        if '<' in value or '>' in value or '\n' in value or '\r' in value or len(value) > 2000:
            raise ValueError('A public biography must be one bounded plain-text paragraph: ' + key)
        result[path] = value + '\n'
    return result
