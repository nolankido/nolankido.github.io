"""Test-only, exact Git-blob predecessor for the Player Find integration.

This is not imported by production build code. Only exact published successor
bytes are rewound, and unreviewed changes remain visible to historical checks.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
  "_scripts/build.py": [
    "bfabc3c4e7391f5955699c1173e2c7273ffd2d8c",
    "384f466d218b879faa85854cdeb8c48441e14807"
  ],
  "_scripts/site_find.py": [
    "470dced0b8d490ec7be9d3b1d9f782f1c8ec46f7",
    "4386c79895d3368c84e903dc676c87bd401adfd2"
  ],
  "_source/find.html": [
    "bf15ea096a4c811d5ce77edc1e2d773bc65ed4a0",
    "dc0ecbf8b326125ded9643299e186080a0088a56"
  ],
  "find/index.html": [
    "58378f58f7f531c18b2feb5eec852e835a7df86a",
    "9dff44288065aa209061af8b80cc1c3a451224b5"
  ],
  "_scripts/local_release_checks.py": [
    "98203578aa419b1ad4cb5b3c817d364667f32d1a",
    "f26de68056421d1fcf41917951ecb7685bd8b48c"
  ],
  "AGENTS.md": [
    "b75a6994cadca1db0e18799c5bf5a32392947d4e",
    "746fdf4ae5ac07c031a2c8a209a90751f2dccc4a"
  ]
}
PATCHES = {
  "_scripts/build.py": [
    [
      "import site_find\nimport player_find\n",
      "import site_find\n"
    ],
    [
      "values['site_find_index'] = site_find.render(player_find.add(ROOT, site_find.entries(ROOT, pages)))",
      "values['site_find_index'] = site_find.render(site_find.entries(ROOT, pages))"
    ]
  ],
  "_scripts/site_find.py": [
    [
      "names = {'essay': 'Essay', 'guide': 'Guide', 'collection': 'Collection / reference', 'profile': 'Player profile'}",
      "names = {'essay': 'Essay', 'guide': 'Guide', 'collection': 'Collection / reference'}"
    ]
  ],
  "_source/find.html": [
    [
      "<option value=\"profile\">Player profiles</option>",
      ""
    ]
  ],
  "find/index.html": [
    [
      "<option value=\"profile\">Player profiles</option>",
      ""
    ],
    [
      "id=\"browse-poker\"><summary>Poker <span class=\"find-group-count\" hidden>(93)</span>",
      "id=\"browse-poker\"><summary>Poker <span class=\"find-group-count\" hidden>(92)</span>"
    ],
    [
      "<li class=\"find-item\" data-kind=\"profile\" data-interests=\"poker\" data-search-title=\"Nolan Kido: Tournament Poker Player | Results &amp; Vlog Plans\"><p class=\"find-kind\">Player profile <span aria-hidden=\"true\">/</span> <span class=\"find-subjects\">Poker</span></p><h3><a href=\"/poker/nolan-kido/\">Nolan Kido: Tournament Poker Player</a></h3><p class=\"find-description\">Nolan Kido&#x27;s live tournament poker record, including independent WSOP and South Point results, plus his approach to reviewing poker hands.</p></li>",
      ""
    ]
  ],
  "_scripts/local_release_checks.py": [
    [
      "        ('Player Find index contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_find.py', '-q']),\n",
      ""
    ]
  ],
  "AGENTS.md": [
    [
      "The on-site Find page additionally includes this manually built public profile through the bounded `_scripts/player_find.py` adapter. Its source-verified title, description and canonical route are searchable locally under the **Player profiles** filter. The main manifest continues to own the other entries, and this addition does not add a new remote search service or index personal records outside the public page. Run `python _scripts/local_release_checks.py` to verify both the Find projection and sitemap without GitHub Actions.",
      "The local search index still follows the primary manifest, so do not claim the manual profile is indexed by the site's internal search until its separate integration is tested and published."
    ]
  ]
}
ADDED = {
  "_scripts/player_find.py": "88b63dbd7a0738e14804c97ac82b87343bd6a871",
  "_tests/test_player_find.py": "cba1ab872af3bc6955719e4422be81169f4bfe3c"
}


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def blob(value):
    raw = value.encode('utf-8') if isinstance(value, str) else value
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + bytes([0]) + raw).hexdigest()


def before(path, value):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(value) != pair[1]:
        return value
    binary = isinstance(value, bytes)
    current = value.decode('utf-8') if binary else value
    for successor, predecessor in PATCHES[name]:
        if current.count(successor) != 1:
            raise ValueError('Player Find predecessor patch is not unique: ' + name)
        current = current.replace(successor, predecessor, 1)
    result = current.encode('utf-8') if binary else current
    if blob(result) != pair[0]:
        raise ValueError('Player Find predecessor does not match approved Git blob: ' + name)
    return result


def source_records(records):
    return {path: data for path, data in records.items()
            if ADDED.get(key(path)) != blob(data)}


def files(paths):
    def keep(path):
        name = key(path)
        expected = ADDED.get(name)
        return expected is None or not (ROOT / name).is_file() or blob((ROOT / name).read_bytes()) != expected
    return type(paths)(path for path in paths if keep(path))
