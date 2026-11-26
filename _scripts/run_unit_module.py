#!/usr/bin/env python3
"""Run one discovered unittest module and emit its actual test-result counts."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

RESULT_PREFIX = 'LOCAL_UNIT_RESULT: '
RESULT_FIELDS = ('tests', 'passed', 'skipped', 'expected_failures',
                 'failures', 'errors', 'unexpected_successes')


class CountingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed += 1


def valid_record(record) -> bool:
    return (isinstance(record, dict) and set(record) == set(RESULT_FIELDS)
            and all(type(value) is int and value >= 0 for value in record.values())
            and record['passed'] <= record['tests'])


def outcome(record) -> str:
    """A skipped or expected-failing module is not evidence of a passing test."""
    if not valid_record(record):
        return 'ERROR'
    if any(record[name] for name in ('failures', 'errors', 'unexpected_successes')):
        return 'FAIL'
    if record['passed']:
        return 'PASS'
    if record['tests'] or record['skipped'] or record['expected_failures']:
        return 'INCOMPLETE'
    return 'ERROR'


def main(filename: str) -> int:
    if (not filename.startswith('test_') or not filename.endswith('.py')
            or any(char in filename for char in '/\\*?[]') or '..' in filename):
        raise ValueError('Expected one exact unittest module filename')
    # Match the repository import context of python -m unittest discover.
    sys.path.insert(0, str(Path.cwd()))
    suite = unittest.defaultTestLoader.discover('_tests', pattern=filename)
    result = unittest.TextTestRunner(verbosity=0, resultclass=CountingResult).run(suite)
    record = {'tests': result.testsRun, 'passed': result.passed,
              'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
              'failures': len(result.failures), 'errors': len(result.errors),
              'unexpected_successes': len(result.unexpectedSuccesses)}
    print(RESULT_PREFIX + json.dumps(record, sort_keys=True), flush=True)
    return {'PASS': 0, 'FAIL': 1, 'INCOMPLETE': 2, 'ERROR': 2}[outcome(record)]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: run_unit_module.py test_module.py')
    raise SystemExit(main(sys.argv[1]))
