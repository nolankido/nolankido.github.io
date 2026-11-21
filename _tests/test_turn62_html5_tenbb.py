"""Turn 62: the published 10 BB Playbook must receive the real HTML5 release check.

This covers a previously omitted standalone route, without altering the page,
the canonical metadata, its course content, or the normal release process.
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
sys.path.insert(0, str(ROOT / "_tests"))

import build
import check_html5
import check_live
import tenbb_companion


class Turn62TenBBHTML5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.paths = check_html5.publication_paths(ROOT, cls.pages)
        cls.page = (ROOT / tenbb_companion.OUTPUT).read_text(encoding="utf-8")

    def test_playbook_is_part_of_the_full_html5_release_inventory(self):
        # There are six other manual standalone pages, two book pages,
        # a book catalog, and the separately authored 10 BB Playbook.
        self.assertEqual(len(self.paths), len(self.pages) + 10)
        self.assertEqual(self.paths[tenbb_companion.ROUTE], tenbb_companion.OUTPUT)
        self.assertEqual(tenbb_companion.record(ROOT)["route"], tenbb_companion.ROUTE)

    def test_all_live_registered_canonical_html_routes_reach_html5_check(self):
        # The live inventory is the independent release target registry.
        # Keep canonical slash routes and .html pages such as /404.html,
        # but exclude downloadable .html worksheets from page coverage.
        live_pages = {
            route for route, (status, body) in check_live.targets(ROOT).items()
            if status == 200
            and (route.endswith("/") or
                 (route.endswith(".html") and not route.startswith("/downloads/")))
            and body.lstrip().lower().startswith(b"<!doctype html")
        }
        self.assertEqual(set(self.paths), live_pages)

    def test_published_playbook_parses_as_html5(self):
        self.assertTrue(self.page.lstrip().lower().startswith("<!doctype html"))
        self.assertEqual(check_html5.parse_errors(self.page), [])

    def test_html5_checker_detects_a_malformed_playbook(self):
        self.assertEqual(self.page.count("</main>"), 1)
        broken = self.page.replace("</main>", "</div></main>", 1)
        self.assertNotEqual(broken, self.page)
        self.assertNotEqual(check_html5.parse_errors(broken), [])

    def test_duplicate_route_cannot_hide_the_manual_page(self):
        duplicated = self.pages + [{"path": tenbb_companion.ROUTE}]
        with self.assertRaisesRegex(ValueError, "10 BB Playbook duplicates"):
            check_html5.publication_paths(ROOT, duplicated)

    def test_manual_runner_invokes_this_regression_and_html5_parser(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("'test_turn62_html5_tenbb.py'", runner)
        self.assertIn("['_tests/check_html5.py']", runner)
        # These checks remain local. No repository-authored Actions workflows.
        forbidden = ROOT / ".github" / "workflows"
        self.assertFalse(forbidden.exists() and any(
            p.is_file() and p.suffix.lower() in {".yml", ".yaml"}
            for p in forbidden.iterdir()
        ))


if __name__ == "__main__":
    unittest.main()
