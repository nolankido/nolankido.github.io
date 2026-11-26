"""PBG-05: link semantics and strict read-only Amazon click-path provenance."""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import poker_book_click_path_audit as audit

FILES = (
    audit.LEDGER, audit.PRIVACY,
    *audit.ROUTES,
    *audit.SOURCE_FILES.values(),
)


def fixture() -> tuple[TemporaryDirectory, Path]:
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    for relative in FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, path)
    return tmp, root


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(before) != 1:
        raise AssertionError("Mutation fixture not present exactly once")
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


class BookClickPathAuditTests(unittest.TestCase):
    def test_live_checkout_has_all_six_exact_link_contracts(self):
        data = audit.audit(ROOT)
        self.assertEqual(data["status"], "pass", data["errors"])
        self.assertEqual(data["link_contracts_expected"], 6)
        self.assertEqual(data["link_contracts_verified"], 6)
        self.assertEqual(data["tracked_link_contracts_verified"], 5)
        self.assertEqual(data["untracked_link_contracts_verified"], 1)
        self.assertEqual(len(data["routes"]), 4)
        self.assertTrue(all(x["public_source_equal"] for x in data["routes"]))

    def test_three_distinct_author_supplied_asins_not_invented(self):
        ledger = json.loads((ROOT / audit.LEDGER).read_text(encoding="utf-8"))
        urls = audit.author_destinations(ledger)
        self.assertEqual(set(urls), set(audit.ASINS))
        for slug, asin in audit.ASINS.items():
            self.assertTrue(urls[slug].endswith("/dp/" + asin))

    def test_linked_html_has_browser_native_fallback_without_js(self):
        for relative in audit.ROUTES:
            with self.subTest(route=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotIn("umami.track(", content)
                self.assertNotIn("onclick=", content)
                self.assertNotIn("window.location=", content)
                tracked = any(event is not None for _, event, _ in audit.ROUTES[relative])
                self.assertEqual(content.count("https://cloud.umami.is/script.js"), int(tracked))
                if not tracked:
                    self.assertNotIn("data-umami-", content)

    def test_no_measured_clicks_purchases_or_attribution_claims(self):
        data = audit.audit(ROOT)
        for key in ("analytics_events_received", "amazon_detail_page_verified",
                    "attribution_tag_available", "kdp_attributed_orders"):
            self.assertIsNone(data[key])
        self.assertIn("does not click the link", data["interpretation"])

    def test_wrong_destination_fails_closed(self):
        tmp, root = fixture()
        try:
            relative = "books/index.html"
            amazon = "https://www.amazon.com/Works-Human-Decides-Nolan-Kido-ebook/dp/B0HSF8K76R"
            replace_once(root / relative, amazon, "https://www.amazon.com/dp/B0INVENTED")
            self.assertEqual(audit.audit(root)["status"], "fail")
        finally:
            tmp.cleanup()

    def test_source_public_byte_mismatch_fails_closed(self):
        tmp, root = fixture()
        try:
            relative = "books/one-workflow-at-a-time/index.html"
            replace_once(root / relative,
                         'data-umami-event-source="book-page-hero"',
                         'data-umami-event-source="books-catalog"')
            report = audit.audit(root)
            self.assertEqual(report["status"], "fail")
            self.assertTrue(any("source and published HTML differ" in err for err in report["errors"]))
        finally:
            tmp.cleanup()

    def test_event_name_or_source_tampering_fails_closed(self):
        for original, forged in (
            ('data-umami-event="poker-book-kindle-amazon-click"',
             'data-umami-event="non-approved-event"'),
            ('data-umami-event="poker-book-kindle-amazon-click" data-umami-event-source="books-catalog"',
             'data-umami-event="poker-book-kindle-amazon-click" data-umami-event-source="user-email"'),
        ):
            with self.subTest(forged=forged):
                tmp, root = fixture()
                try:
                    replace_once(root / "books/index.html", original, forged)
                    self.assertEqual(audit.audit(root)["status"], "fail")
                finally:
                    tmp.cleanup()

    def test_unsanctioned_tracking_or_amazon_link_fails(self):
        tmp, root = fixture()
        try:
            doc = root / "books/index.html"
            data = doc.read_text(encoding="utf-8")
            data = data.replace("</main>", '<a href="https://www.amazon.com/dp/B0INVENTED">Other</a></main>')
            doc.write_text(data, encoding="utf-8")
            self.assertEqual(audit.audit(root)["status"], "fail")
        finally:
            tmp.cleanup()

    def test_ledger_without_author_provenance_is_rejected(self):
        tmp, root = fixture()
        try:
            p = root / audit.LEDGER
            data = json.loads(p.read_text(encoding="utf-8"))
            edition = next(x for x in data["works"] if x["slug"] == "how-to-play-no-limit-texas-holdem")
            edition["formats"][0]["author_supplied_asin"] = "B0INVENTED"
            p.write_text(json.dumps(data), encoding="utf-8")
            report = audit.audit(root)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["link_contracts_verified"], 0)
        finally:
            tmp.cleanup()

    def test_tracking_disclosure_cannot_be_removed(self):
        tmp, root = fixture()
        try:
            p = root / audit.PRIVACY
            replace_once(p, "A click is not proof of an Amazon purchase",
                         "A click guarantees an Amazon purchase")
            self.assertTrue(any(x.startswith("privacy:") for x in audit.audit(root)["errors"]))
        finally:
            tmp.cleanup()

    def test_cli_output_is_parsable_and_read_only(self):
        out = StringIO()
        with redirect_stdout(out):
            rc = audit.main(["--root", str(ROOT)])
        self.assertEqual(rc, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["scope"], "read_only_local_link_contracts")
        self.assertEqual(report["link_contracts_verified"], 6)

    def test_manual_release_suite_registers_audit(self):
        runner = (ROOT / "_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_pbg05_book_click_path_audit.py", runner)
        self.assertIn("_scripts/poker_book_click_path_audit.py", runner)
        folder = ROOT / ".github/workflows"
        self.assertFalse(folder.exists() and any(
            x.suffix.lower() in (".yaml", ".yml") for x in folder.iterdir()))


if __name__ == "__main__":
    unittest.main()
