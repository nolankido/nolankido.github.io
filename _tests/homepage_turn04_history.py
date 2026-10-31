"""Test-only exact predecessor for the Turn 4 homepage reader-path revision.

Older release capsules must receive their original source and generated home
bytes. Only the two reviewed complete successors can be rewound; unrecognized
changes remain visible rather than being silently accepted as old releases.
"""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = '9c0a2126c2f73cb4f3a14f759cccab4e0ec18c57'
REVISIONS = {
    '_source/home.html': (
        'b139831fc4c8c9bc763eef2662925e64485fe70007cf923ec61c623802ef649e',
        'f4ec91d422d04775080691076a74b375e72a2c0674a6a2a829fbe4a122d330a4',
    ),
    'index.html': (
        '1ca755dc96a03feee7dc0921c822c5627e390cc4ce47b8c9cbfaa982e021b9af',
        'e9a95f88b640143c47b179110d656172869b609dc3d7428cffb1af3b419f70ae',
    ),
}
CAPTION_NEW_END = ' I also build software tools and play tournament poker.</p>\n'
CAPTION_OLD_END = '</p>\n'
NAV_OLD = (
    '    <div class="link-row identity-actions"><a class="button" href="/technology/#ai-works-human-decides">How the approach works <span aria-hidden="true">→</span></a>'
    '<a class="text-link" href="/about/">Meet Nolan <span aria-hidden="true">→</span></a>'
    '<a class="text-link" href="/technology/">Explore practical AI <span aria-hidden="true">→</span></a></div>\n'
)
NAV_NEW = (
    '    <nav class="link-row identity-actions" aria-label="Explore Nolan Kido\'s work and interests">'
    '<a class="button" href="/technology/#ai-works-human-decides">Practical AI in real life <span aria-hidden="true">→</span></a>'
    '<a class="text-link" href="/technology/#technology-projects">Technology projects <span aria-hidden="true">→</span></a>'
    '<a class="text-link" href="/poker/#watch">Poker with Nolan <span aria-hidden="true">→</span></a>'
    '<a class="text-link" href="/about/">Meet Nolan <span aria-hidden="true">→</span></a></nav>\n'
)


def digest(data: str | bytes) -> str:
    return sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def key(path: str | Path) -> str:
    target = Path(path)
    if target.is_absolute():
        try:
            target = target.relative_to(ROOT)
        except ValueError:
            return target.as_posix()
    return target.as_posix()


def before(path: str | Path, data: str | bytes) -> str | bytes:
    """Rewind only an exact, reviewed successor to its verified old bytes."""
    pair = REVISIONS.get(key(path))
    if pair is None or digest(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    content = data.decode('utf-8') if binary else data
    if content.count(CAPTION_NEW_END) != 1 or content.count(NAV_NEW) != 1:
        raise ValueError('Invalid Turn 4 homepage successor boundaries')
    previous = content.replace(CAPTION_NEW_END, CAPTION_OLD_END, 1).replace(NAV_NEW, NAV_OLD, 1)
    if digest(previous) != pair[0]:
        raise ValueError('Invalid Turn 4 homepage predecessor digest')
    return previous.encode('utf-8') if binary else previous
