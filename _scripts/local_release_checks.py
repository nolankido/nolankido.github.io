#!/usr/bin/env python3
"""Run website release checks locally without any CI or network actions."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def forbid_workflows() -> None:
    folder = ROOT / '.github' / 'workflows'
    active = sorted(p for p in folder.glob('*') if p.is_file() and p.suffix.lower() in {'.yml', '.yaml'})
    if active:
        raise RuntimeError('GitHub Actions are prohibited for this site: ' + ', '.join(str(p.relative_to(ROOT)) for p in active))


def check(label: str, args: list[str]) -> bool:
    print(f'\n=== {label} ===', flush=True)
    result = subprocess.run([sys.executable, *args], cwd=ROOT, check=False)
    print(f'{label}: {"PASS" if result.returncode == 0 else "FAIL"}', flush=True)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Run full historical unit tests and HTML parsing (can take time)')
    parser.add_argument('--browser', action='store_true', help='Also run local browser scripts; requires Playwright and browsers')
    args = parser.parse_args()
    try:
        forbid_workflows()
    except RuntimeError as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        return 2

    tasks = [
        ('Deterministic build', ['_scripts/build.py', '--check']),
        ('Player profile build', ['_scripts/build_player_profile.py', '--check']),
        ('Portland video companion build', ['_scripts/build_poker_episode.py', '--check']),
        ('Local laptop guide build', ['_scripts/build_local_laptop_case.py', '--check']),
        ('Local laptop article and loopback contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_local_laptop_case.py', '-q']),
        ('Portland video companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_portland_episode.py', '-q']),
        ('Two narrated real hand records', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_real_portland_hands.py', '-q']),
        ('Public Poker and combined RSS receipts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_manual_poker_feed.py', '-q']),
        ('Player sitemap and live-target contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_sitemap.py', '-q']),
        ('Player Find index contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_find.py', '-q']),
        ('SEO and metadata', ['_scripts/check_search.py']),
    ]
    if args.full:
        tasks.extend([
            ('HTML5 parsing', ['_tests/check_html5.py']),
            ('Full unit suite', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_*.py', '-q']),
        ])
    else:
        tasks.append(('Poker evidence regressions', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_visibility_poker_player*.py', '-q']))
    if args.browser:
        suites = sorted((ROOT / '_tests').glob('*_browser.py'))
        standalone = ROOT / '_tests' / 'browser.py'
        if standalone.is_file():
            suites.insert(0, standalone)
        tasks.extend((f'Local browser: {p.stem}', [str(p.relative_to(ROOT))]) for p in suites)
    successes = [check(label, command) for label, command in tasks]
    count = sum(successes)
    print(f'\nLocal release checks: {count}/{len(tasks)} passed. No GitHub Actions were invoked.')
    return 0 if all(successes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
