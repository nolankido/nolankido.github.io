"""Require committed test coverage in local releases, with no network access."""
from pathlib import Path
import subprocess


def committed_test_names(root: Path) -> set[str]:
    result = subprocess.run(
        ['git', '-C', str(root), 'ls-tree', '-z', '--name-only', 'HEAD:_tests'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError('Cannot read committed test inventory from HEAD:_tests')
    names = result.stdout.decode('utf-8').split('\0')
    return {name for name in names if name}


def is_unit(name: str) -> bool:
    return name.startswith('test_') and name.endswith('.py')


def is_browser(name: str) -> bool:
    return name == 'browser.py' or name.endswith('_browser.py')


def require_committed(root: Path, expected: set[str], actual: set[str], kind: str) -> None:
    if not expected:
        raise ValueError('No committed ' + kind + ' test inventory')
    missing = sorted(expected - actual)
    if missing:
        raise ValueError('Missing committed ' + kind + ' tests: ' + ', '.join(missing))
    unsafe = sorted(name for name in actual if (root / '_tests' / name).is_symlink()
                    or not (root / '_tests' / name).is_file())
    if unsafe:
        raise ValueError('Non-regular ' + kind + ' test files: ' + ', '.join(unsafe))


def verify_tracked_units(root: Path, names: list[str]) -> None:
    """Do not let a preexisting deletion shrink the full unit inventory."""
    expected = {name for name in committed_test_names(root) if is_unit(name)}
    require_committed(root, expected, set(names), 'unit')


def browser_inventory(root: Path) -> list[str]:
    """Keep every committed browser script, including the primary suite."""
    expected = {name for name in committed_test_names(root) if is_browser(name)}
    if 'browser.py' not in expected or not any(name.endswith('_browser.py') for name in expected):
        raise ValueError('Committed browser inventory must include the primary and specialized suites')
    actual = {p.name for p in (root / '_tests').glob('*.py') if is_browser(p.name)}
    require_committed(root, expected, actual, 'browser')
    return ['browser.py', *sorted(actual - {'browser.py'})]
