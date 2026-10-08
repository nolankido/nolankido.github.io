"""Maintainable discovery metadata and progressive enhancement contracts."""
from html import escape
from pathlib import Path
import unittest
from test_site import ROOT, Page, build
import poker_resources as resources
import check_live


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = resources.load(ROOT)
        cls.outputs = build.build_outputs()
        cls.html = cls.outputs[Path('poker/resources/index.html')]

    def test_each_detailed_kind_has_exactly_one_discovery_type(self):
        for e in self.entries:
            self.assertEqual(sum(e['kind'] in kinds for _, kinds in resources.FORMATS.values()), 1)
            self.assertIn(resources.resource_format(e), resources.FORMATS)

    def test_unknown_kind_fails_instead_of_disappearing_from_filters(self):
        with self.assertRaises(ValueError):
            resources.resource_format({'kind':'Unreviewed new format'})

    def test_buckets_are_disjoint(self):
        kinds = [kind for _, values in resources.FORMATS.values() for kind in values]
        self.assertEqual(len(kinds),len(set(kinds)))

    def test_cards_expose_exact_metadata_without_removing_descriptions(self):
        for e in self.entries:
            rendered = resources.card(e)
            for value in ['data-level="'+e['level']+'"', 'data-format="'+resources.resource_format(e)+'"',
                          escape(e['description']), e['reviewed_on']]:
                self.assertIn(value,rendered)
            if e['notes']: self.assertIn(escape(e['notes']),rendered)
            self.assertLess(rendered.index('reader-card-meta'),rendered.index('resource-description'))

    def test_domains_are_displayed_without_tracking_links(self):
        from urllib.parse import urlsplit
        for e in self.entries:
            rendered=resources.card(e)
            self.assertIn(urlsplit(e['url']).hostname.removeprefix('www.'),rendered)
            self.assertEqual(len([a for a in Page(rendered).tags('a') if a.get('rel')=='external']),1)

    def test_permalinks_are_native_and_labeled(self):
        for e in self.entries:
            links=[a for a in Page(resources.card(e)).tags('a') if 'data-resource-jump' in a]
            self.assertEqual(len(links),1)
            self.assertEqual(links[0]['href'],'#resource-'+e['id'])
            self.assertEqual(links[0]['aria-label'],'Link to listing: '+e['title'])

    def test_beginner_path_is_free_and_beginner_appropriate(self):
        ids=resources.STARTING_PATHS[0][2]
        by_id={e['id']:e for e in self.entries}
        for ident in ids:
            self.assertEqual(by_id[ident]['access'],'Free')
            self.assertIn(by_id[ident]['level'],{'Beginner','All levels'})

    def test_every_topic_has_context_and_related_local_reading(self):
        self.assertEqual(set(resources.TOPIC_HELP),set(resources.CATEGORIES))
        for key,(_,route,_) in resources.CATEGORIES.items():
            self.assertIn(escape(resources.TOPIC_HELP[key]),self.html)
            self.assertIn('href="'+route+'"',self.html)

    def test_resource_styles_are_scoped_to_only_this_route(self):
        for path,html in self.outputs.items():
            if path.suffix=='.html':
                self.assertEqual('/assets/poker-resources.css?v=' in html,str(path)=='poker/resources/index.html')
        self.assertIn('/assets/poker-resources.css',check_live.targets())

    def test_filters_and_print_start_hidden_and_have_native_labels(self):
        tags=Page(self.html)
        self.assertIn('hidden',next(a for a in tags.tags('div') if a.get('id')=='resource-controls'))
        self.assertIn('hidden',next(a for a in tags.tags('button') if a.get('id')=='resource-print'))
        labels={a.get('for') for a in tags.tags('label')}
        self.assertTrue({'resource-search','resource-format','resource-level'}<=labels)
        self.assertIn('All levels',self.html)

    def test_support_shortcuts_stay_outside_filtered_sections(self):
        intro=self.html.split('id="basics"')[0]
        self.assertIn('href="#resource-ncpg"',intro)
        self.assertIn('href="#resource-gamcare-support"',intro)

    def test_catalogue_stays_the_single_source_of_resource_data(self):
        links=[a for a in Page(self.html).tags('a') if a.get('rel')=='external']
        self.assertCountEqual([a['href'] for a in links],[e['url'] for e in self.entries])
        self.assertEqual(resources.supplement(self.entries),resources.supplement(self.entries))


if __name__=='__main__': unittest.main()
