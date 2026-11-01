"""Exact, test-only predecessor for the manual player sitemap release.

Only Git-blob-identical reviewed successor files can be rewound. An unreviewed
change passes through unchanged, retaining the original frozen release tests.
No production builder imports this module and no CI service is required.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISIONS = {
  "_scripts/build.py": {
    "old": "093886a74d810fb87503be4c14e0b42b2253693a",
    "new": "bfabc3c4e7391f5955699c1173e2c7273ffd2d8c",
    "edits": [
      [
        1432,
        "import player_sitemap\n",
        ""
      ],
      [
        33606,
        "    player_sitemap.add_to_sitemap(sitemap, ROOT)\n",
        ""
      ]
    ]
  },
  "_scripts/check_search.py": {
    "old": "088925da89b0aa09de6210adedbd963d2da46db0",
    "new": "f458778af008272cddc49c6f830375e980de9df7",
    "edits": [
      [
        533,
        "import player_sitemap\n",
        ""
      ],
      [
        2204,
        "    try:\n        manual_profile = player_sitemap.record(root)\n    except (OSError, ValueError, KeyError, TypeError) as exc:\n        errors.append('Manual poker-player profile: ' + str(exc))\n        manual_profile = None\n    if manual_profile is not None:\n        expected_indexed.add(manual_profile[0])\n        totals['manual_player_pages'] += 1\n",
        ""
      ]
    ]
  },
  "_scripts/check_live.py": {
    "old": "b716a68c9b6323466cea7bd32f11c94c308d1e45",
    "new": "5743bb6064180a814fe97044e54ec948ea40cd47",
    "edits": [
      [
        274,
        "import player_sitemap\n",
        ""
      ],
      [
        803,
        "    manual_profile = player_sitemap.record(root)\n    if manual_profile is not None:\n        route = player_sitemap.ROUTE\n        if route in result:\n            raise ValueError('Manual player page duplicates an existing generated route')\n        result[route] = (200, (root / player_sitemap.RELATIVE).read_bytes())\n",
        ""
      ]
    ]
  },
  "_scripts/local_release_checks.py": {
    "old": "a83b6cff47eb31755c5ed49b245c578dd64e46c5",
    "new": "98203578aa419b1ad4cb5b3c817d364667f32d1a",
    "edits": [
      [
        1537,
        "        ('Player sitemap and live-target contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_sitemap.py', '-q']),\n",
        ""
      ]
    ]
  },
  "_tests/test_site.py": {
    "old": "3676272010e672c191bf612bfe0917ff2e4c8e0c",
    "new": "ca1c7f7aca64b4ed30231aca09a94cb2772d5af1",
    "edits": [
      [
        5589,
        "        expected = {'https://nolankido.com' + p['path'] for p in self.manifest if not p.get('noindex')}\n        manual = build.player_sitemap.record(ROOT)\n        if manual is not None:\n            expected.add(manual[0])\n        self.assertEqual(set(urls), expected)\n        self.assertEqual(len(urls), len(set(urls)))\n",
        "        self.assertEqual(set(urls), {'https://nolankido.com' + p['path'] for p in self.manifest if not p.get('noindex')})\n"
      ]
    ]
  },
  "sitemap.xml": {
    "old": "4a391f335d3c67db4b04ad110c2596e83befe146",
    "new": "a9b30b5c1b60379b68cad7ba8b90a1ca2b26af5a",
    "edits": [
      [
        22889,
        "  <url>\n    <loc>https://nolankido.com/poker/nolan-kido/</loc>\n    <lastmod>2026-11-01</lastmod>\n  </url>\n",
        ""
      ]
    ]
  }
}
ADDED_FILES = {
  "_scripts/player_sitemap.py": "10595fe6c8908499876402a591daf53234e847dc",
  "_tests/test_player_sitemap.py": "2f92405261b0651f47dd14ffbaee41d97e9b00d4"
}
PLAYER_BLOB = "fb56af5af00bd8f27ab4f98296586eddeb97043f"
PROFILE_ROUTE = "/poker/nolan-kido/"


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    record = REVISIONS.get(key(path))
    if record is None or blob(data) != record["new"]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    for start, newer, older in reversed(record["edits"]):
        if current[start:start + len(newer)] != newer:
            raise ValueError("Reviewed player sitemap predecessor patch mismatch")
        current = current[:start] + older + current[start + len(newer):]
    result = current.encode("utf-8") if binary else current
    if blob(result) != record["old"]:
        raise ValueError("Reviewed player sitemap predecessor blob mismatch")
    return result


def source_records(records):
    """Remove only exact brand-new helper files from historic inventories."""
    return {path: data for path, data in records.items()
            if ADDED_FILES.get(key(path)) != blob(data)}


def files(paths):
    def retain(path):
        name = key(path)
        digest = ADDED_FILES.get(name)
        return digest is None or not (ROOT / name).is_file() or blob((ROOT / name).read_bytes()) != digest
    return type(paths)(path for path in paths if retain(path))


def live_targets(records):
    def keep(route, response):
        return not (route == PROFILE_ROUTE and isinstance(response, tuple)
                    and len(response) == 2 and type(response[0]) is int
                    and response[0] == 200 and isinstance(response[1], bytes)
                    and blob(response[1]) == PLAYER_BLOB)
    return {route: response for route, response in records.items() if keep(route, response)}
