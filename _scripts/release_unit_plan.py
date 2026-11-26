"""Keep full local release coverage while avoiding duplicate focused unit runs."""
from pathlib import Path
import json


def full_unit_plan(tasks, folder: Path):
    """Retain non-unit checks and require every focused module in the full inventory."""
    from check_historical_batches import discover
    inventory = discover('test_*.py', folder=folder)
    if not inventory:
        raise ValueError('No historical unit modules discovered')
    retained = []
    focused = set()
    groups = 0
    for label, args in tasks:
        if args[:3] != ['-m', 'unittest', 'discover']:
            retained.append((label, args))
            continue
        if len(args) != 8 or args[3:6] != ['-s', '_tests', '-p'] or args[7] != '-q':
            raise ValueError('Unsupported focused discovery command: ' + label)
        matches = discover(args[6], folder=folder)
        if not matches or not set(matches).issubset(inventory):
            raise ValueError('Focused release group not covered by full inventory: ' + label)
        focused.update(matches)
        groups += 1
    return retained, inventory, groups, len(focused)


def check_inventory(path: Path, actual: list[str]) -> None:
    """Require the exact sorted module inventory from this release invocation."""
    expected = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(expected, list) or any(not isinstance(x, str) for x in expected):
        raise ValueError('Expected inventory must be a list of module filenames')
    if not expected or expected != sorted(set(expected)):
        raise ValueError('Expected inventory must be nonempty, sorted and unique')
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise ValueError('Full unit inventory changed; missing: ' + repr(missing) + '; extra: ' + repr(extra))
