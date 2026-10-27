"""Check the published-source review against its sources and preserved record."""
from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import unittest

import html5lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import practical_path

SNAPSHOT = 'https://github.com/nolankido/nolankido.github.io/blob/a64bc51b6a39405a1ba59fbc589a9e190fce6229/'
REPORT = '_reports/website-growth/turn-04-public-source-plan.md'
REPORT_SHA256 = 'e4d41ce543774ee592cbd442612e4cc3c1f4deaa910a0913a427bccd1e61ac50'
RESULT_SHA256 = 'd29f19043ac0a438873a721f609d5ab22e9cea9662fa21c06d3aac1b4cf6cef8'
WORKBOOK_SHA256 = 'c793d8d20e0006f522d081d34b901cc97d5bb741c2dd4861e2eceb20b8966e23'
SOURCES = {
    'S1': ('weekly-reset', 'Check the commitments that have a real source',
           'notes-source-commitments',
           'Copy only what affects the coming week. Keep verified dates separate from ideas and requests that have not been agreed.'),
    'S2': ('weekly-reset', 'Reduce the list before organizing it',
           'notes-source-action',
           'Then choose one next action that is concrete enough to begin.'),
    'S3': ('decide-what-matters', 'State the decision without smuggling in the answer',
           'notes-source-deadline',
           'Do not create an artificial deadline simply to make the situation easier to summarize.'),
    'S4': ('what-to-decide-yourself', 'Separate expression from intention',
           'notes-source-promises',
           'The tool should not decide what you feel, what responsibility you accept, or what you are promising.'),
    'S5': ('weekly-reset', 'Stop when the page has done its job',
           'notes-source-stop',
           'The reset is finished when you can see the important commitments, understand the next action, and identify what you are deliberately leaving alone.'),
}


def text(node):
    return ' '.join(''.join(node.itertext()).split())


class PublicSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '_source/technology/home.html').read_text(encoding='utf-8')
        cls.outputs = build.build_outputs()
        cls.documents = {
            'source': html5lib.parseFragment(cls.source, namespaceHTMLElements=False),
            'generated': html5lib.parse(cls.outputs[Path('technology/index.html')], namespaceHTMLElements=False),
        }
        cls.guides = {entry['slug']: entry for entry in
                      json.loads((ROOT / '_source/living-well/launch.json').read_text())['entries']}
        cls.original_report = (ROOT / REPORT).read_text(encoding='utf-8')

    def one(self, document, identifier):
        matches = document.findall('.//*[@id="' + identifier + '"]')
        self.assertEqual(len(matches), 1, identifier)
        return matches[0]

    def original_outline(self):
        section = self.original_report.split('## Initial AI-assisted outline, October 17, 2026\n', 1)[1].split('\n## ', 1)[0]
        lines = re.findall(r'^\d+\. (.+)$', section, re.M)
        self.assertEqual(len(lines), 5)
        return lines

    def test_five_exact_excerpts_match_the_named_source_sections(self):
        for kind, document in self.documents.items():
            case = self.one(document, 'notes-to-plan-case')
            quotes = case.findall('.//q[@data-case-source]')
            self.assertEqual([q.get('data-case-source') for q in quotes], list(SOURCES), kind)
            for quote in quotes:
                label = quote.get('data-case-source')
                slug, heading, identifier, expected = SOURCES[label]
                with self.subTest(document=kind, source=label):
                    self.assertEqual(''.join(quote.itertext()), expected)
                    sections = [s for s in self.guides[slug]['sections'] if s['heading'] == heading]
                    self.assertEqual(len(sections), 1)
                    self.assertTrue(any(expected in paragraph for paragraph in sections[0]['paragraphs']))
                    record = self.one(case, identifier)
                    self.assertIn(heading, text(record))
                    self.assertIs(record.find('.//q'), quote)
                    self.assertIsNotNone(record.find('.//a[@href="/living-well/' + slug + '/"]'))

    def test_review_date_and_snapshot_do_not_relabel_the_original_exercise(self):
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                case = self.one(document, 'notes-to-plan-case')
                sources = self.one(case, 'notes-case-source-record')
                self.assertIsNotNone(sources.find('.//a[@href="' + SNAPSHOT + '_source/living-well/launch.json"]'))
                dates = sources.findall('.//time')
                self.assertEqual([(d.get('datetime'), text(d)) for d in dates],
                                 [('2026-10-27', 'October 27, 2026')])
                self.assertIn('They document this follow-up review.', text(sources))
                self.assertIn('On October 17, 2026, an AI-assisted editorial pass', text(case))
                self.assertIsNotNone(case.find('.//a[@href="' + SNAPSHOT + REPORT + '"]'))
        page = next(p for p in build.public_pages() if p['id'] == 'technology')
        self.assertEqual(page['updated'], '2026-10-27')
        self.assertFalse(page.get('date'))

    def test_recorded_brief_matches_the_unmodified_october_17_report(self):
        self.assertEqual(sha256((ROOT / REPORT).read_bytes()).hexdigest(), REPORT_SHA256)
        section = self.original_report.split('## Actual task issued to the assistant for this editorial pass\n', 1)[1].split('\n## ', 1)[0]
        recorded = '\n'.join(line[2:] for line in section.splitlines() if line.startswith('> '))
        self.assertTrue(recorded)
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                brief = self.one(document, 'notes-case-recorded-brief')
                self.assertEqual(''.join(brief.itertext()), recorded)
                self.assertEqual(brief.get('cite'), SNAPSHOT + REPORT)

    def test_original_five_line_outline_and_four_step_result_are_preserved(self):
        outline = self.original_outline()
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                case = self.one(document, 'notes-to-plan-case')
                revisions = self.one(case, 'notes-case-revisions')
                self.assertEqual([text(li) for li in revisions.find('ol').findall('li')], outline)
                result = case.find('.//div[@class="brief-scope"]')
                self.assertEqual(len(result.find('ol').findall('li')), 4)
                self.assertIn('Still unknown:', text(result))
        original_result = re.search(r'<div class="brief-scope">.*?</div>', self.source, re.S)[0]
        self.assertEqual(sha256(original_result.encode()).hexdigest(), RESULT_SHA256)

    def test_each_correction_names_its_original_instruction_and_source_constraints(self):
        expected_links = {
            'S1': ['#notes-source-commitments'], 'S2': ['#notes-source-action'],
            'S3': ['#notes-source-deadline', '#notes-source-promises'],
            'S4': ['#notes-source-promises'], 'S5': ['#notes-source-stop'],
        }
        for kind, document in self.documents.items():
            case = self.one(document, 'notes-to-plan-case')
            checks = self.one(case, 'notes-case-checks').findall('li')
            self.assertEqual([li.get('data-case-check') for li in checks], list(SOURCES), kind)
            for check, initial in zip(checks, self.original_outline()):
                label = check.get('data-case-check')
                with self.subTest(document=kind, correction=label):
                    self.assertEqual(text(check.find('./p/strong')), '“' + initial + '”')
                    self.assertEqual([a.get('href') for a in check.findall('.//a')], expected_links[label])
                    for field in ['Check:', 'Correction:', 'Still for a person:']:
                        self.assertIn(field, [text(s) for s in check.findall('./p/strong')])

    def test_original_anchors_and_native_private_decision_path_remain_available(self):
        anchors = ['notes-to-plan-case', 'notes-to-plan-title', 'notes-case-sources',
                   'notes-case-revisions', 'notes-case-result', 'notes-case-limits']
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                for identifier in anchors:
                    self.one(document, identifier)
                case = self.one(document, 'notes-to-plan-case')
                jumps = case.find('.//div[@class="entry-jumps"]')
                self.assertEqual([a.get('href') for a in jumps.findall('a')], [
                    '#notes-case-sources', '#notes-case-revisions', '#notes-case-result',
                    '#notes-case-decision', '#notes-case-limits',
                ])
                for identifier in ['notes-case-source-record', 'notes-case-revisions']:
                    disclosure = self.one(case, identifier)
                    self.assertEqual(disclosure.tag, 'details')
                    self.assertNotIn('open', disclosure.attrib)
                    self.assertIsNotNone(disclosure.find('summary'))
                self.one(case, 'notes-case-decision')
                decisions = case.find('.//ol[@aria-label="Your decision before using the note"]')
                self.assertEqual([text(li.find('strong')) for li in decisions.findall('li')],
                                 ['Keep:', 'Confirm:', 'Leave out:'])
                for tag in ['form', 'input', 'textarea', 'script']:
                    self.assertEqual(case.findall('.//' + tag), [])

    def test_limits_do_not_claim_human_adoption_or_observed_results(self):
        for kind, document in self.documents.items():
            plain = text(self.one(document, 'notes-to-plan-case'))
            for statement in [
                'not a personal weekly schedule or evidence that a visitor saved time',
                'No calendar was accessed, no person was assigned work, and no result was field-tested.',
                'not a reconstructed output from a separate AI service',
                'a separate human reviewer has not signed off, and no participant used the plan.',
                'not a measured personal productivity benefit, learner study, or verified improvement',
                'Accepting some of it, changing it, or leaving it unused are all available choices.',
                'Leave observed time and results blank until you have them',
            ]:
                with self.subTest(document=kind, statement=statement):
                    self.assertIn(statement, plain)

    def test_case_reuses_the_exact_existing_workbook(self):
        raw = (ROOT / practical_path.WORKBOOK).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), WORKBOOK_SHA256)
        self.assertEqual(self.outputs[practical_path.WORKBOOK].encode(), raw)
        for kind, document in self.documents.items():
            with self.subTest(document=kind):
                case = self.one(document, 'notes-to-plan-case')
                downloads = case.findall('.//a[@download]')
                self.assertEqual(len(downloads), 1)
                self.assertEqual(downloads[0].get('href'), '/' + practical_path.WORKBOOK.as_posix())


if __name__ == '__main__':
    unittest.main()
