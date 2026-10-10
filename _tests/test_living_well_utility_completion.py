"""Static practical starters, truthful labels, and outcome-led discovery."""
from copy import deepcopy
from html import escape
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import living_well as lw
import living_well_utility as utility

class CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = lw.load(ROOT)
        cls.guides = [e for e in cls.entries if e.get('utility')]
        cls.outputs = build.build_outputs()

    def test_seven_static_starters_show_inputs_outcomes_and_finish(self):
        self.assertEqual(len(self.guides), 7)
        for e in self.guides:
            page = self.outputs[Path('living-well') / e['slug'] / 'index.html']
            with self.subTest(slug=e['slug']):
                self.assertIn(escape(e['outcome']), page)
                for field in utility.FIELDS:
                    self.assertIn(escape(e['utility'][field]), page)
                self.assertIn('<pre>' + escape(e['utility']['starter']) + '</pre>', page)
                self.assertIn('class="lw-preview" open', page)
                for anchor in ['useful-result', 'plain-text-starter']:
                    self.assertEqual(page.count('id="' + anchor + '"'), 1)
                    self.assertEqual(page.count('href="#' + anchor + '"'), 1)
                self.assertNotRegex(page, r'<(?:form|input|textarea|iframe)\b')
                self.assertIn('No generative AI required', page)

    def test_original_readings_do_not_gain_utility_claims(self):
        for e in self.entries:
            if not e.get('series'):
                self.assertEqual(utility.brief(e), '')
                self.assertEqual(utility.starter(e), '')
                self.assertEqual(utility.outline(e, 'unchanged'), 'unchanged')
        hub = next(e for e in self.entries if e['slug'] == utility.SERIES)
        self.assertEqual(utility.brief(hub), '')
        self.assertEqual(lw.entry_label(hub), 'Practical starting point')

    def test_schema_rejects_missing_wrong_or_unsupported_claims(self):
        base = self.guides[0]
        variants = []
        for field in utility.FIELDS:
            e = deepcopy(base); del e['utility'][field]; variants.append(e)
            e = deepcopy(base); e['utility'][field] = ' '; variants.append(e)
            e = deepcopy(base); e['utility'][field] = 2; variants.append(e)
        for field, value in [('series', 'unknown'), ('series', ''), ('kind', 'essay'),
                             ('evidence_status', 'firsthand-result'), ('outcome', '')]:
            e = deepcopy(base); e[field] = value; variants.append(e)
        e = deepcopy(base); e['utility']['starter'] = 'x' * 2501; variants.append(e)
        e = deepcopy(base); e['utility']['unknown'] = 'unsupported'; variants.append(e)
        for e in variants:
            with self.subTest(variant=e):
                with self.assertRaises(ValueError):
                    utility.validate(e)

    def test_new_plain_text_fields_are_escaped_not_executed(self):
        e = deepcopy(self.guides[0])
        value = '<b title="quote">Literal & private</b>'
        e['outcome'] = value
        e['utility'] = {key: value for key in utility.FIELDS}
        text = utility.brief(e) + utility.starter(e)
        self.assertNotIn(value, text)
        self.assertIn(escape(value), text)
        self.assertNotIn('<b ', text)

    def test_templates_contribute_to_reading_estimates(self):
        e = deepcopy(self.guides[0])
        before = lw.minutes(e)
        e['utility']['starter'] += ' ordinary' * 500
        self.assertGreater(lw.minutes(e), before)
        for field in utility.FIELDS:
            self.assertIn(self.guides[0]['utility'][field], utility.reading_text(self.guides[0]))

    def test_prominent_home_and_nonduplicate_practical_discovery(self):
        home = self.outputs[Path('living-well/index.html')]
        guides = self.outputs[Path('living-well/guides/index.html')]
        self.assertIn('id="technology-in-ordinary-life"', home)
        self.assertIn('href="/living-well/technology-for-real-life/"', home)
        self.assertIn('id="real-life-guides"', guides)
        section = re.search(r'<section[^>]+aria-labelledby="real-life-guides".*?</section>', guides).group(0)
        self.assertEqual(section.count('class="lw-card"'), 7)
        for e in self.guides:
            self.assertEqual(guides.count('href="/living-well/' + e['slug'] + '/"'), 1)
        for collection in ['everyday-tools', 'everyday-ai', 'digital-life', 'care']:
            page = self.outputs[Path('living-well/free-resources') / collection / 'index.html']
            self.assertIn('id="put-a-resource-to-use"', page)
            self.assertIn('href="/living-well/technology-for-real-life/"', page)

if __name__ == '__main__':
    unittest.main(verbosity=2)
