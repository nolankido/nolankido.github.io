"""Turn 107: make optional study questions discoverable without indexing answers."""
from pathlib import Path
import ast
from html.parser import HTMLParser
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
from poker_optional_summary import optional_summary_sections

SAT = 'Advanced example (extra reading time): satellite split pots and ties. Can two calls with the same chip equity have different seat values?'
BOUNTY = 'Advanced example (extra reading time): mystery bounty draw inventory. What is a mystery bounty worth after the jackpot has been drawn?'
EXAMPLES = (
    ('satellite-bubble-seat-equity', 'sat-tie-branch', SAT, '2179 / 2310'),
    ('bounty-knockout-equity', 'bounty-mystery-draw', BOUNTY, '$1,000 / 3'),
)


def detail(anchor='advanced-case', title='Find this study question', answer='DO NOT INDEX ANSWER'):
    return (f'<details id="{anchor}" data-reading-optional="true">'
            f'<summary>{title}</summary><div><p>{answer}</p></div></details>')


def passage(anchor, title):
    return {'anchor': anchor, 'title': title, 'text': title}


def guide_text_class():
    """Run the actual extraction class without importing full site dependencies."""
    path = ROOT / '_scripts/poker_finder.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'GuideText')
    context = {'HTMLParser': HTMLParser, 're': re, 'optional_summary_sections': optional_summary_sections}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), context)
    return context['GuideText']


class OptionalSummaryStandalone(unittest.TestCase):
    def test_only_the_visible_title_becomes_searchable(self):
        self.assertEqual(optional_summary_sections(detail()), [passage('advanced-case', 'Find this study question')])
        self.assertNotIn('DO NOT INDEX ANSWER', repr(optional_summary_sections(detail())))

    def test_ordinary_practice_and_unmarked_details_stay_excluded(self):
        for variant in ('', 'false', 'True'):
            text = detail().replace('data-reading-optional="true"', f'data-reading-optional="{variant}"')
            self.assertEqual(optional_summary_sections(text), [])
        self.assertEqual(optional_summary_sections(detail().replace(' data-reading-optional="true"', '')), [])

    def test_hidden_navigation_and_nested_disclosures_stay_excluded(self):
        for opening, closing in (('<nav>', '</nav>'), ('<div hidden>', '</div>'),
                                 ('<section aria-hidden="true">', '</section>'),
                                 ('<details><summary>Practice</summary>', '</details>'),
                                 ('<template>', '</template>'), ('<noscript>', '</noscript>')):
            with self.subTest(opening=opening):
                text = opening + detail('excluded') + closing + detail('visible')
                self.assertEqual(optional_summary_sections(text), [passage('visible', 'Find this study question')])
        hidden = detail().replace('<details ', '<details hidden ')
        self.assertEqual(optional_summary_sections(hidden), [])
        nested = detail('outer', answer=detail('inner', title='Nested spoiler'))
        self.assertEqual(optional_summary_sections(nested), [passage('outer', 'Find this study question')])

    def test_missing_unsafe_duplicate_and_empty_titles_fail_closed(self):
        for text in (detail(''), detail('bad anchor'), detail('bad#id'), detail('UPPER'),
                     detail() + detail(), detail(title=' '),
                     detail().replace('<summary>Find this study question</summary>', ''),
                     detail().replace('<summary>', '<summary hidden>'),
                     detail().replace('<summary>', '<summary aria-hidden="true">'),
                     detail(title='Question <span hidden>secret answer</span>'),
                     detail().replace('</summary>', ''),
                     detail().replace('</details>', ''),
                     '<details data-reading-optional="true" id="broken"/>'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                optional_summary_sections(text)

    def test_whitespace_entities_and_document_order_are_preserved(self):
        source = detail('first', '  Chips &amp; prizes?\n Read more. ') + detail('second', 'Mystery draw')
        self.assertEqual(optional_summary_sections(source), [passage('first', 'Chips & prizes? Read more.'),
                                                             passage('second', 'Mystery draw')])

    def test_unrelated_closing_tag_does_not_release_hidden_container(self):
        source = '<div hidden></aside>' + detail('secret') + '</div>' + detail('shown')
        self.assertEqual(optional_summary_sections(source), [passage('shown', 'Find this study question')])

    def test_guide_core_sections_unchanged_and_only_summary_appended(self):
        guide = guide_text_class()
        core = '<h2 id="first">First heading</h2><p>First text.</p><h2 id="last">Last heading</h2><p>Last text.</p>'
        before = guide(core).sections
        after = guide(core.replace('<h2 id="last">', detail() + '<h2 id="last">')).sections
        self.assertEqual(after, before + [passage('advanced-case', 'Find this study question')])
        self.assertNotIn('DO NOT INDEX ANSWER', repr(after))

    def test_optional_anchor_cannot_collide_with_core_section(self):
        guide = guide_text_class()
        with self.assertRaisesRegex(ValueError, 'Optional study anchor duplicates a guide section'):
            guide('<h2 id="advanced-case">Heading</h2><p>Core.</p>' + detail())


class OptionalSummarySiteIntegration(unittest.TestCase):
    def test_two_real_guides_and_generated_finder_passages(self):
        import poker_finder
        finder = (ROOT / 'poker/find/index.html').read_text(encoding='utf-8')
        from html import escape
        for slug, anchor, title, answer in EXAMPLES:
            with self.subTest(slug=slug):
                authored = (ROOT / '_source/poker' / (slug + '.html')).read_text(encoding='utf-8')
                public = (ROOT / 'poker' / slug / 'index.html').read_text(encoding='utf-8')
                for text in (authored, public):
                    self.assertEqual(optional_summary_sections(text), [passage(anchor, title)])
                sections = poker_finder.GuideText(authored).sections
                self.assertEqual(sections[-1], passage(anchor, title))
                self.assertNotIn(answer, repr(sections))
                markup = f'<p data-finder-passage data-anchor="{anchor}" data-heading="{escape(title, quote=True)}">{escape(title)}</p>'
                self.assertEqual(finder.count(markup), 1)
                card_start = finder.index('data-id="poker-' + slug + '"')
                card = finder[card_start:finder.index('</article>', card_start)]
                self.assertIn(markup, card)
                self.assertNotIn(answer, card)
                self.assertEqual(card.count(f'data-anchor="{anchor}"'), 1)
        self.assertIn('301 entries available.', finder)
        self.assertIn('Labelled optional study summaries are searchable; their answer bodies remain excluded.', finder)

    def test_builder_and_manual_runner(self):
        import build
        paths = ('poker/find/index.html', 'poker/satellite-bubble-seat-equity/index.html',
                 'poker/bounty-knockout-equity/index.html')
        outputs = build.build_outputs()
        for path in paths:
            self.assertEqual(outputs[Path(path)], (ROOT / path).read_text(encoding='utf-8'), path)
        self.assertIn('test_turn107_optional_finder_summaries.py',
                      (ROOT / '_scripts/local_release_checks.py').read_text(encoding='utf-8'))
        self.assertNotIn('sat-tie-branch', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn('bounty-mystery-draw', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
