"""Reverse the frozen Technology opening navigation at its two exact paths."""
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def change():
    return json.loads((ROOT / '_tests/technology-jumps-change.json').read_text())


def before(path, data):
    if str(path) not in {'_source/technology/home.html', 'technology/index.html'}:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    c = change()
    text = text.replace(c['new'], c['old'], 1)
    return text.encode() if binary else text
