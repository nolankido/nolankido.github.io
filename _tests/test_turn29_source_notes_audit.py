"""Turn 29: authentic public notes-to-actions record plus a bounded source gate."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
import build

SOURCE = ROOT / "_source/technology/organize-public-notes.html"
PUBLIC = ROOT / "technology/organize-public-notes/index.html"
CHECKER = ROOT / "downloads/source-notes-audit.py"
RECORD = ROOT / "downloads/public-notes-action-record.txt"
SECTION_ID = "notes-repro-audit"
BASE = "061324dc666d4a5be9b1c0d63b1f11305cbb96f6"


def get_section(doc):
    start = '<section class="section folio-row" id="' + SECTION_ID + '"'
    if doc.count(start) != 1:
        raise AssertionError("Missing or duplicate notes audit section")
    offset = doc.index(start)
    return doc[offset:doc.index("</section>", offset) + len("</section>")]


class Tags(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise AssertionError("Unbalanced HTML: " + tag)


def run_checker(*args):
    return subprocess.run([sys.executable, str(CHECKER), *map(str, args)],
                          capture_output=True, text=True)


def mutate_row(text, task, update):
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith("| " + task + " |")]
    if len(matches) != 1:
        raise AssertionError("Expected one original task line: " + task)
    index = matches[0]
    pieces = lines[index].rstrip("\n").split("|")
    if len(pieces) != 6:
        raise AssertionError("Unexpected archived Markdown table structure")
    update(pieces)
    lines[index] = "|".join(pieces) + "\n"
    return "".join(lines)


class NotesReceiptGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.html = PUBLIC.read_text(encoding="utf-8")

    def test_one_documented_case_in_source_and_public_page(self):
        self.assertEqual(get_section(self.source), get_section(self.html))
        section = get_section(self.html)
        self.assertEqual(self.html.count('id="' + SECTION_ID + '"'), 1)
        self.assertEqual(section.count('<tr>'), 5)
        self.assertEqual(section.count('<th scope="row">'), 4)
        self.assertIn("11", section.replace("eleven", "11"))
        self.assertIn("not mistakes observed in the archived AI response", section)
        self.assertIn('href="/downloads/source-notes-audit.py" download', section)
        self.assertIn('href="/downloads/public-notes-action-record.txt" download', section)
        self.assertIn('href="#notes-repro-audit"', self.source)
        self.assertNotIn("\u2014", section)
        self.assertNotIn("<script", section)
        parsed = Tags()
        parsed.feed(section)
        self.assertEqual(parsed.stack, [])

    def test_actual_immutable_public_record_has_eleven_bounded_rows(self):
        record = RECORD.read_text(encoding="utf-8")
        self.assertIn("===== VERBATIM ASSISTANT OUTPUT =====", record)
        self.assertIn("N1: The personal website needs permanent pages", record)
        result = run_checker("--check", RECORD)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        output = json.loads(result.stdout)
        self.assertEqual(output["rows"], 11)
        self.assertEqual(output["flags"], 0)
        self.assertEqual(output["findings"], [])
        self.assertIn("does not establish external truth", output["limit"])

    def test_five_synthetic_controls_have_specific_expected_results(self):
        result = run_checker("--self-test")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertTrue(data["synthetic"])
        self.assertTrue(data["passed"])
        self.assertEqual([row["codes"] for row in data["cases"]],
                         [[], ["STATUS_MISMATCH"], ["SOURCE_MISMATCH"],
                          ["MISSING_BOUNDARY"], ["UNSUPPORTED_DATE"]])
        self.assertIn("not observed AI output mistakes", data["limit"])

    def test_four_mutations_of_archived_rows_are_rejected(self):
        original = RECORD.read_text(encoding="utf-8")
        travel = "Personal travel plan"
        dinner = "Prepare a permanent Dinner on Time page"
        unsupported = "Keep unsupported outcomes and commitments out of the copy"
        altered = [
            (mutate_row(original, travel, lambda cells: cells.__setitem__(4, " ready to prepare ")), "STATUS_MISMATCH"),
            (mutate_row(original, travel, lambda cells: cells.__setitem__(2, cells[2].replace("N6:", "N5:"))), "SOURCE_MISMATCH"),
            (mutate_row(original, dinner, lambda cells: cells.__setitem__(2, cells[2].replace("no runtime AI", "runtime AI"))), "MISSING_BOUNDARY"),
            (mutate_row(original, unsupported, lambda cells: cells.__setitem__(3, cells[3] + "; publish by 2026-12-01")), "UNSUPPORTED_DATE"),
        ]
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "altered.txt"
            for content, flag in altered:
                file.write_text(content, encoding="utf-8")
                result = run_checker("--check", file)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                codes = [row["code"] for row in json.loads(result.stdout)["findings"]]
                self.assertIn(flag, codes)
            file.write_text("not a recorded public response", encoding="utf-8")
            invalid = run_checker("--check", file)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("Input error", invalid.stderr)

    def test_updated_publication_metadata_and_find_are_consistent(self):
        page = next(p for p in build.public_pages() if p["id"] == "organize-public-notes")
        self.assertEqual(page["date"], "2026-10-27")
        self.assertEqual(page["updated"], "2026-11-04")
        schema_text = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.html).group(1)
        schema = json.loads(schema_text)
        self.assertEqual(schema["datePublished"], "2026-10-27")
        self.assertEqual(schema["dateModified"], "2026-11-04")
        self.assertEqual(self.html.count('property="article:modified_time" content="2026-11-04"'), 1)
        self.assertIn('<link rel="canonical" href="https://nolankido.com/technology/organize-public-notes/">', self.html)
        index_html = (ROOT / "find/index.html").read_text(encoding="utf-8")
        data = json.loads(re.search(r'<script type="application/json" id="find-section-data">(.*?)</script>', index_html).group(1))
        rows = data["pages"]["technology"]["organize-public-notes/"]
        offset = rows.index("notes-repro-title")
        self.assertEqual(rows[offset + 1], "Can the action list still be traced to what was actually supplied?")
        self.assertEqual(rows[offset + 2], "notes-reuse")
        loc = "https://nolankido.com/technology/organize-public-notes/"
        xml = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        dates = {
            e.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            e.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            for e in xml
        }
        self.assertEqual(dates[loc], "2026-11-04")
        self.assertEqual(list(dates).count(loc), 1)

    def test_build_owned_outputs_match_the_committed_release(self):
        outputs = build.build_outputs()
        for relative in ("technology/organize-public-notes/index.html",
                         "find/index.html", "sitemap.xml"):
            with self.subTest(path=relative):
                self.assertEqual(outputs[Path(relative)],
                                 (ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
