"""Keep 2012 scholarly evidence distinct from 2026 explanatory writing."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ROUTE = '/about/accounting-research/'
DOI = 'https://doi.org/10.1111/j.1475-679X.2012.00447.x'
MIT = 'https://dspace.mit.edu/entities/publication/9e5c8e82-34b0-4931-a8cc-6ea0ae938829'
SSRN = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1753198'
DISCUSSION = 'https://doi.org/10.1111/j.1475-679X.2012.00446.x'
DISCUSSION_SSRN = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1980697'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


class PublishedAccountingResearchTests(unittest.TestCase):
    def test_single_dated_searchable_article(self):
        pages = json.loads(read('_source/pages.json'))
        matching = [p for p in pages if p['path'] == ROUTE or p['id'] == 'accounting-research']
        self.assertEqual(len(matching), 1)
        item = matching[0]
        self.assertEqual(item['section'], 'about')
        self.assertEqual(item['date'], '2026-11-13')
        self.assertTrue(item['evidence_article'])
        self.assertFalse(item.get('noindex'))
        html = read('about/accounting-research/index.html')
        self.assertIn('rel="canonical" href="https://nolankido.com' + ROUTE + '"', html)
        self.assertIn('article:published_time" content="2026-11-13"', html)
        self.assertNotIn('noindex', html)
        sitemap = ET.fromstring(read('sitemap.xml'))
        matches = [el for el in sitemap.findall('{*}url') if el.findtext('{*}loc') == 'https://nolankido.com' + ROUTE]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].findtext('{*}lastmod'), '2026-11-13')

    def test_scholarship_and_commentary_have_distinct_structured_dates_and_authors(self):
        html = read('about/accounting-research/index.html')
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['author']['@id'], 'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(schema['datePublished'], '2026-11-13')
        paper = schema['about']
        self.assertEqual(paper['@type'], 'ScholarlyArticle')
        self.assertEqual(paper['@id'], DOI)
        self.assertEqual(paper['datePublished'], '2012-03-23')
        self.assertEqual(paper['isPartOf']['name'], 'Journal of Accounting Research')
        self.assertEqual([a['name'] for a in paper['author']], ['Nolan Kido', 'Reining Petacchi', 'Joseph Weber'])
        self.assertEqual(paper['author'][0]['@id'], schema['author']['@id'])
        self.assertEqual(schema['citation'], [DOI, MIT, SSRN, DISCUSSION, DISCUSSION_SSRN])
        self.assertNotIn(DISCUSSION, json.dumps(paper))
        self.assertNotIn(DISCUSSION_SSRN, json.dumps(paper))

    def test_version_of_record_date_is_consistent_with_public_identity(self):
        source = read('_source/about/accounting-research.html')
        public = read('about/accounting-research/index.html')
        history = ('Wiley records the accepted manuscript online February 6, 2012, '
                   'the version of record online March 23, 2012, '
                   'and the issue dated May 2012.')
        self.assertIn(history, source)
        self.assertIn(history, public)
        graph = read('_source/person-schema.jsonld')
        self.assertEqual(graph, read('assets/nolan-kido-identity.jsonld'))
        papers = [node for node in json.loads(graph)['@graph'] if node['@id'] == DOI]
        self.assertEqual(len(papers), 1)
        paper = papers[0]
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">(.*?)</script>', public, re.S).group(1))
        self.assertEqual(paper['datePublished'], '2012-03-23')
        self.assertEqual(schema['about']['datePublished'], paper['datePublished'])
        self.assertEqual(schema['about']['name'], paper['headline'])
        self.assertEqual(schema['about']['author'][0]['@id'], paper['author'][0]['@id'])
        self.assertEqual(schema['about']['pagination'], paper['pageStart'] + '-' + paper['pageEnd'])
        self.assertEqual(schema['datePublished'], '2026-11-13')

    def test_bounded_public_source_and_result_language(self):
        text = read('_source/about/accounting-research.html')
        for expected in ('compensated absences', 'unfunded pension',
                         'systematically lower', 'associated with proxy',
                         'does not by itself identify', 'not</strong> evidence',
                         'not an AI study', 'not a claim about my employment',
                         '2012 article', 'November 2026', DOI, MIT):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)
        self.assertNotIn('\u2014', text)
        self.assertNotIn('the AI paper', text.lower())
        self.assertIn('id="research-table-hint"', text)
        self.assertIn('aria-describedby="research-table-hint"', text)

    def test_reachable_from_home_about_and_project_portfolio(self):
        for path in ('index.html', 'about/index.html', 'projects/index.html'):
            with self.subTest(path=path):
                self.assertIn('href="' + ROUTE + '"', read(path))
        home = read('index.html')
        self.assertIn('href="https://onlinelibrary.wiley.com/doi/10.1111/j.1475-679X.2012.00447.x"', home)
        self.assertIn('href="' + MIT + '"', home)
        self.assertIn('Published research explanation', read('notes/index.html'))

    def test_earlier_working_paper_distinguishes_name_version_and_author_order(self):
        ssrn = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1753198'
        target = '/about/accounting-research/#research-sources'
        for path in ('_source/about/accounting-research.html',
                     'about/accounting-research/index.html'):
            with self.subTest(path=path):
                html = read(path)
                self.assertEqual(html.count('id="research-sources"'), 1)
                records = re.findall(r'<li><strong>Earlier working-paper record:</strong>.*?</li>',
                                     html, re.S)
                self.assertEqual(len(records), 1)
                for phrase in (f'href="{ssrn}"', 'Nolan Y. Kido',
                               'different author order from the journal',
                               'not a second peer-reviewed publication',
                               'journal citation and DOI above',
                               'SSRN citation checked November 26, 2026'):
                    self.assertIn(phrase, records[0])
                self.assertIn(f'href="{DOI}"', html)
                self.assertIn(f'href="{MIT}"', html)
        for path in ('_source/about.html', 'about/index.html'):
            with self.subTest(path=path):
                html = read(path)
                self.assertEqual(html.count(f'href="{target}"'), 1)
                self.assertIn('The earlier working-paper citation uses my name Nolan Y. Kido', html)

    def test_independent_discussion_is_linked_without_changing_research_authorship(self):
        for path in ('_source/about/accounting-research.html',
                     'about/accounting-research/index.html'):
            with self.subTest(path=path):
                document = read(path)
                items = re.findall(r'<li><strong>Independent scholarly discussion:</strong>.*?</li>',
                                   document, re.S)
                self.assertEqual(len(items), 1)
                for phrase in ('Laurence van Lent (2012)', '477–494',
                               'changes in state employment',
                               'separately authored discussion',
                               'not another publication of mine',
                               'not another publication of mine or a replication performed here'):
                    self.assertIn(phrase, items[0])
                self.assertEqual(re.findall(r'href="([^"]+)"', items[0]),
                                 [DISCUSSION, DISCUSSION_SSRN])
                self.assertEqual(document.count(f'href="{DISCUSSION}"'), 1)
                self.assertEqual(document.count(f'href="{DISCUSSION_SSRN}"'), 1)
        schema = json.loads(re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            read('about/accounting-research/index.html'), re.S).group(1))
        self.assertEqual(schema['about']['@id'], DOI)
        self.assertEqual([a['name'] for a in schema['about']['author']],
                         ['Nolan Kido', 'Reining Petacchi', 'Joseph Weber'])
        self.assertEqual(schema['citation'], [DOI, MIT, SSRN, DISCUSSION, DISCUSSION_SSRN])
        self.assertEqual(schema['datePublished'], '2026-11-13')
        self.assertNotIn('dateModified', schema)

    def test_research_evidence_map_and_ai_verification_guide_cross_link(self):
        research = '/about/accounting-research/#research-claims'
        method = '/technology/check-ai-answers/#review-research'
        for path in ('_source/technology/check-ai-answers.html',
                     'technology/check-ai-answers/index.html'):
            with self.subTest(path=path):
                html = read(path)
                self.assertEqual(html.count(f'href="{research}"'), 1)
                self.assertIn('Check the passage supporting each claim;', html)
                self.assertEqual(html.count('id="review-research"'), 1)
        for path in ('_source/about/accounting-research.html',
                     'about/accounting-research/index.html'):
            with self.subTest(path=path):
                html = read(path)
                self.assertEqual(html.count(f'href="{method}"'), 1)
                self.assertEqual(html.count('id="research-claims"'), 1)
                self.assertIn('not an additional empirical result from the 2012 study', html)

    def test_modified_dates_follow_content_changes_only(self):
        pages = {p['path']: p for p in json.loads(read('_source/pages.json'))}
        sitemap = ET.fromstring(read('sitemap.xml'))
        # November 13 is the research explanation's publication date, not
        # the permanent revision date of every page that links to it.
        reviewed = (
            ('/', 'index.html', '2026-11-24'),
            ('/about/', 'about/index.html', '2026-11-24'),
            ('/projects/', 'projects/index.html', '2026-11-18'),
        )
        for route, path, modified in reviewed:
            with self.subTest(route=route):
                self.assertEqual(pages[route]['updated'], modified)
                self.assertNotIn('date', pages[route])
                rows = [url for url in sitemap
                        if url.findtext('{*}loc') == 'https://nolankido.com' + route]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0].findtext('{*}lastmod'), modified)
                schema = json.loads(re.search(
                    r'<script type="application/ld\+json">(.*?)</script>',
                    read(path), re.S).group(1))
                self.assertNotIn('datePublished', schema)
                if route == '/about/':
                    # The ProfilePage has no verified modification timestamp.
                    self.assertEqual(schema['@type'], 'ProfilePage')
                    self.assertNotIn('dateModified', schema)
                else:
                    self.assertEqual(schema['dateModified'], modified)


if __name__ == '__main__':
    unittest.main()
