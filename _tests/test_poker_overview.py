"""Whole-Poker wayfinding and discoverability, independent of the renderer's counters."""
from collections import deque
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json
import re
import unittest
from test_site import ROOT, Page, build
import poker_reading
import poker_navigation
import poker_finder

class PokerOverviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build_outputs()
        cls.pages = [p for p in build.public_pages() if p['path'].startswith('/poker/')]
        cls.guides = build.poker_library.load(ROOT, build.public_pages())
        cls.resources = build.poker_resources.load(ROOT)
        cls.topics = build.poker_topics.load(ROOT, build.public_pages(), cls.guides, cls.resources)

    def test_every_poker_page_has_one_active_section(self):
        for p in self.pages:
            nav = poker_navigation.section_navigation(p)
            self.assertEqual(nav.count('aria-current='), 1, p['path'])
            self.assertEqual(len(Page(nav).tags('a')), 7, p['path'])
        nav = poker_navigation.section_navigation({'path':'/poker/study-calculators/'})
        self.assertIn('href="/poker/study/" aria-current="location"', nav)

    def test_one_breadcrumb_trail_without_losing_targets(self):
        for p in self.pages:
            text = self.outputs[build.output_path(p['path'])]
            self.assertNotIn('class="viewer-breadcrumb"', text, p['path'])
            self.assertEqual(text.count('aria-label="Breadcrumb"'), p['path'] != '/poker/', p['path'])
        with self.assertRaises(ValueError):
            poker_navigation.clean_body('<nav class="viewer-breadcrumb"><a id="old">Keep</a></nav>')
        ordinary = '<nav aria-label="Continue"><a href="/poker/">Home</a></nav>'
        self.assertEqual(poker_navigation.clean_body(ordinary), ordinary)

    def test_outlines_include_first_sections_and_exclude_hidden_spoilers(self):
        source = '<h2 id="one">First <em>step</em></h2><details><h2 id="answer">Spoiler</h2></details><nav><h2 id="nav">No</h2></nav><div aria-hidden="true"><h2 id="hidden">No</h2></div><h2 id="two">Second</h2>'
        outline = poker_reading.section_outline(source)
        self.assertEqual([a['href'] for a in Page(outline).tags('a')], ['#one','#two'])
        for p in self.pages:
            if not p.get('poker_guide') and p['path'] != '/poker/reviewing-a-hand/': continue
            source = (ROOT / '_source' / p['source']).read_text()
            headings = poker_reading.VisibleHeadings(source).headings
            if len(headings) < 2: continue
            text = self.outputs[build.output_path(p['path'])]
            outline = re.search(r'<details class="reader-outline">.*?</details>',text,re.S).group()
            self.assertEqual([a['href'] for a in Page(outline).tags('a')], ['#'+i for i,_ in headings], p['path'])
        study = self.outputs[Path('poker/cash-game-study-path/index.html')]
        self.assertIn('href="#session-one"',study)

    def test_library_uses_the_same_ten_subjects_and_exact_memberships(self):
        text = self.outputs[Path('poker/library/index.html')]
        parsed = Page(text)
        buttons = [a for a in parsed.tags('button') if 'data-filter' in a]
        self.assertEqual([a['data-filter'] for a in buttons], ['all']+[t['id'] for t in self.topics])
        cards = [a for _,a in parsed.elements if 'data-library-card' in a and 'data-topics' in a]
        # The library is in catalogue order, which is independent of topic order.
        self.assertEqual(len(cards), len(self.guides))
        for guide, card in zip(self.guides,cards):
            expected = {t['id'] for t in self.topics if guide['slug'] in t['primary_guides']+t['related_guides']}
            self.assertEqual(set(card['data-topics'].split()), expected, guide['slug'])

    def test_all_topic_sources_have_direct_no_script_links(self):
        for t in self.topics:
            text = self.outputs[Path('poker/topics')/t['id']/'index.html']
            index = re.search(r'<details class="poker-details topic-all-sources">.*?</details>',text,re.S).group()
            urls = [a['href'] for a in Page(index).tags('a') if a.get('rel') == 'external']
            self.assertEqual(set(urls),{r['url'] for r in t['resources']},t['id'])
            self.assertEqual(len(urls),len(set(urls)))
            for r in t['resources']:
                self.assertIn('/poker/resources/#resource-'+r['id'], index)
                self.assertIn(build.text(r['access']),index)

    def test_every_poker_destination_is_within_three_links_of_home(self):
        routes = {p['path'] for p in self.pages}
        graph = {}
        for p in self.pages:
            graph[p['path']] = set()
            for a in Page(self.outputs[build.output_path(p['path'])]).tags('a'):
                u = urlsplit(urljoin('https://nolankido.com'+p['path'],a.get('href','')))
                if u.netloc == 'nolankido.com' and u.path in routes: graph[p['path']].add(u.path)
        distances={'/poker/':0};todo=deque(distances)
        while todo:
            current=todo.popleft()
            for route in graph[current]:
                if route not in distances:
                    distances[route]=distances[current]+1;todo.append(route)
        self.assertEqual(set(distances),routes)
        self.assertLessEqual(max(distances.values()),3)

    def test_search_prose_excludes_aria_hidden_content(self):
        sections=poker_finder.GuideText('<h2 id="first">First</h2><p>Visible.</p><span aria-hidden="true">SECRET</span><h2 id="second">Second</h2><p>Next.</p>').sections
        text=' '.join(s['text'] for s in sections)
        self.assertNotIn('SECRET',text);self.assertIn('Visible.',text)

    def test_updated_reader_metadata_is_not_disguised_as_publication_date(self):
        item=self.guides[0]
        text=build.poker_library.reader_meta({'path':item['route'],'date':'2026-01-01','updated':'2026-10-08'},self.guides)
        self.assertIn('Updated',text);self.assertIn('datetime="2026-10-08"',text)
        self.assertNotIn('January',text)

    def test_task_entry_points_precede_download_sections(self):
        text=self.outputs[Path('poker/study/index.html')]
        self.assertLess(text.index('id="study-routes"'),text.index('id="hand-review"'))
        home=self.outputs[Path('poker/index.html')]
        self.assertNotIn('class="topic-card"',home)
        self.assertIn('aria-label="Poker topics"',home)
        self.assertIn('class="topic-card"',self.outputs[Path('poker/topics/index.html')])

if __name__ == '__main__': unittest.main()
