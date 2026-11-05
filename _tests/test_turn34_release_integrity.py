"""Release regressions: truthful dates, complete coverage and failing checks."""
import ast
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
import shutil
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build
import check_live
import check_search
import local_release_checks
import poker_standoff_episode as standoff
import search_entrypoints
import check_html5

ORIGIN = "https://nolankido.com"


def companion_fixture(root, urls):
    for relative in (standoff.SOURCE, standoff.OUTPUT):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    sitemap_fixture(root, urls)


def sitemap_fixture(root, urls):
    xml = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        ET.SubElement(ET.SubElement(xml, "url"), "loc").text = url
    (root / "sitemap.xml").write_text(ET.tostring(xml, encoding="unicode"), encoding="utf-8")


class ReleaseIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()

    def test_older_search_copy_cannot_backdate_a_content_revision(self):
        pages = deepcopy(self.pages)
        page = next(p for p in pages if p["id"] == "start-here")
        page["updated"] = "2026-11-04"
        original = deepcopy(pages)
        revised = search_entrypoints.metadata(pages, ROOT)
        self.assertEqual(next(p for p in revised if p["id"] == "start-here")["updated"],
                         "2026-11-04")
        self.assertEqual(pages, original)

    def test_newer_search_copy_keeps_its_own_substantive_revision(self):
        page = {"id": "start-here", "updated": "2026-10-28"}
        entry = {"seo_title": "Test title", "description": "Test description",
                 "updated": "2026-11-04"}
        with patch.object(search_entrypoints, "load", return_value={"start-here": entry}):
            revised = search_entrypoints.metadata([page], ROOT)
        self.assertEqual(revised[0]["updated"], "2026-11-04")
        self.assertEqual(page, {"id": "start-here", "updated": "2026-10-28"})
        self.assertNotIn("entry_summary", entry)

    def test_both_companions_are_in_the_real_search_inventory(self):
        result = check_search.audit(ROOT, self.pages, ORIGIN)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["manual_episode_pages"], 2)
        self.assertEqual(result["manual_laptop_guides"], 1)

    def test_standoff_sitemap_rejects_missing_duplicate_and_unknown_routes(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            companion_fixture(root, [standoff.URL])
            self.assertEqual(check_search.audit(root, [], ORIGIN)["status"], "pass")
            for urls in ([], [standoff.URL, standoff.URL], [standoff.URL, ORIGIN + "/unknown/"]):
                with self.subTest(urls=urls):
                    sitemap_fixture(root, urls)
                    result = check_search.audit(root, [], ORIGIN)
                    self.assertIn("Sitemap must contain each indexable canonical exactly once",
                                  result["errors"])

    def test_missing_source_or_invalid_canonical_cannot_pass_the_search_audit(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            companion_fixture(root, [standoff.URL])
            source = root / standoff.SOURCE
            source.unlink()
            result = check_search.audit(root, [], ORIGIN)
            self.assertTrue(any("Manual video companion" in e for e in result["errors"]))
            shutil.copyfile(ROOT / standoff.SOURCE, source)
            page = root / standoff.OUTPUT
            original = page.read_text(encoding="utf-8")
            broken = original.replace('<link rel="canonical" href="' + standoff.URL + '">',
                                      '<link rel="canonical" href="https://example.invalid/">', 1)
            self.assertNotEqual(broken, original)
            page.write_text(broken, encoding="utf-8")
            self.assertEqual(check_search.audit(root, [], ORIGIN)["status"], "fail")

    def test_html_parser_covers_every_source_owned_page(self):
        paths = check_html5.publication_paths(ROOT, self.pages)
        self.assertEqual(len(paths), len(self.pages) + 5)
        for route in ("/poker/nolan-kido/", "/poker/episodes/portland-meadows-ep1/",
                      standoff.ROUTE, "/technology/local-ai-gaming-laptop/",
                      "/technology/review-reply-evidence-audit/"):
            self.assertIn(route, paths)
            self.assertEqual(check_html5.parse_errors((ROOT / paths[route]).read_text()), [])

    def test_html_inventory_rejects_partial_and_duplicate_manual_publication(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            companion_fixture(root, [standoff.URL])
            with self.assertRaisesRegex(ValueError, "duplicates"):
                check_html5.publication_paths(root, [{"path": standoff.ROUTE}])
            (root / standoff.SOURCE).unlink()
            with self.assertRaisesRegex(ValueError, "requires source"):
                check_html5.publication_paths(root, [])

    def test_a_failed_standoff_builder_fails_the_release_checklist(self):
        invoked = []
        def run(command, **kwargs):
            invoked.append(command)
            return SimpleNamespace(returncode=1 if "_scripts/build_standoff_episode.py" in command else 0)
        with patch.object(sys, "argv", ["local_release_checks.py"]), \
                patch.object(local_release_checks.subprocess, "run", side_effect=run), \
                redirect_stdout(StringIO()):
            self.assertEqual(local_release_checks.main(), 1)
        self.assertTrue(any("_scripts/build_standoff_episode.py" in c for c in invoked))
        self.assertTrue(any("_tests/check_html5.py" in c for c in invoked))

    def test_a_missing_test_suite_cannot_report_a_successful_empty_run(self):
        with TemporaryDirectory() as temp, \
                patch.object(local_release_checks, "ROOT", Path(temp)), \
                patch.object(local_release_checks.subprocess, "run") as run, \
                redirect_stdout(StringIO()):
            self.assertFalse(local_release_checks.check("Missing contracts", [
                "-m", "unittest", "discover", "-s", "_tests", "-p", "test_missing.py", "-q"]))
            run.assert_not_called()

    def test_recent_evidence_downloads_have_exact_manual_live_targets(self):
        targets = check_live.targets()
        for filename in ("source-notes-audit.py", "identity-evidence-gate.py",
                         "identity-evidence-case-workbook.md", "nolan-kido-public-profile-kit.md"):
            self.assertEqual(targets["/downloads/" + filename],
                             (200, (ROOT / "downloads" / filename).read_bytes()))

    def test_python_helpers_remain_parseable(self):
        for folder in ("_scripts", "_tests"):
            for path in (ROOT / folder).glob("*.py"):
                with self.subTest(path=str(path.relative_to(ROOT))):
                    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_mobile_repairs_preserve_every_original_command(self):
        for relative, count in (("_source/poker/portland-meadows-ep1.html", 1),
                                ("_source/technology/local-ai-gaming-laptop.html", 6),
                                ("_source/technology/review-reply-evidence-audit.html", 1)):
            old = subprocess.check_output([
                "git", "show", "80170a3909e2a70fcbbb34ea667953b2af77e45f:" + relative],
                cwd=ROOT, text=True)
            current = (ROOT / relative).read_text(encoding="utf-8")
            before = re.findall(r"<pre>(.*?)</pre>", old, re.S)
            after = re.findall(r"<pre>(.*?)</pre>", current, re.S)
            self.assertEqual(len(before), count)
            self.assertEqual(before, after, relative)


if __name__ == "__main__":
    unittest.main()
