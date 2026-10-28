"""Public introductions and preserved, ordered, cache-versioned core styling."""
import choice_history
from copy import deepcopy
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import re
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import build
import check_live
import core_styles
import public_profile
import visibility_sprint_history
import visibility_discovery_history

class Links(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.links=[]; self.feed(html)
    def handle_starttag(self, tag, attrs):
        if tag == 'link': self.links.append(dict(attrs))

class PublicProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site=json.loads((ROOT/'_source/site.json').read_text())
        cls.outputs=build.build_outputs()
        cls.html=cls.outputs[Path('bio/index.html')]

    def test_original_public_body_identity_feeds_and_css_are_preserved(self):
        baseline=json.loads((ROOT/'_tests/public-profile-baseline.json').read_text())
        records=[]
        previous_outputs=visibility_sprint_history.outputs(self.outputs)
        for path in sorted((p for p in previous_outputs if p.suffix=='.html' and p.as_posix() not in baseline['body_exclusions'] and p.as_posix() not in choice_history.NEW_OUTPUTS), key=lambda p:p.as_posix()):
            raw=choice_history.before(path,previous_outputs[path]).encode()
            body=re.search(rb'<body\b[^>]*>(.*?)</body>',raw,re.S).group(1)
            records.append((path.as_posix(),sha256(body).hexdigest()))
        self.assertEqual(len(records),baseline['unchanged_body_count'])
        self.assertEqual(sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest(),baseline['unchanged_body_signature'])
        for path,digest in baseline['unchanged_files'].items():
            self.assertEqual(sha256(choice_history.read(path)).hexdigest(),digest,path)

    def test_biographies_are_exact_existing_identity_text(self):
        # Identity file is also pinned by the pre-existing preservation tests.
        exports=public_profile.exports(self.site)
        self.assertEqual(len(exports),2)
        for key,path in public_profile.EXPORTS.items():
            self.assertEqual(exports[path],self.site[key]+'\n')
            self.assertEqual(self.outputs[path].encode(),(ROOT/path).read_bytes())
            self.assertIn(escape(self.site[key]),self.html)
            self.assertIn('href="/'+path.as_posix()+'" download',self.html)
        self.assertIn('id="profile-short-text" tabindex="-1"',self.html)
        self.assertIn('id="profile-long-text" tabindex="-1"',self.html)

    def test_scope_and_no_new_profile_claims(self):
        schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',self.html)[1])
        self.assertEqual(schema['about']['@id'],'https://nolankido.com/about/#nolan-kido')
        self.assertEqual(set(schema['about']),{'@type','@id','name','url'})
        for forbidden in ['<form','data-umami-event','sameAs','jobTitle','award','affiliation']:
            self.assertNotIn(forbidden,self.html)
        for page in build.public_pages():
            content=self.outputs[build.output_path(page['path'])]
            for asset in ['public-profile.js','public-profile.css']:
                self.assertEqual('/assets/'+asset+'?v=' in content,page['id']=='bio')
        for route in ['/technology/task-brief/','/technology/checking-ai-website-changes/','/notes/keep-the-judgment/','/about/','/contact/']:
            self.assertIn('href="'+route+'"',self.html)

    def test_copy_controls_progressively_enhanced_and_bounded(self):
        buttons=re.findall(r'<button[^>]*data-profile-copy="([^"]+)"[^>]*>',self.html)
        self.assertEqual(buttons,['profile-short-text','profile-long-text','profile-site-url'])
        self.assertEqual(len(re.findall(r'<button[^>]+hidden>',self.html)),3)
        self.assertIn('aria-live="polite"',self.html)
        js=(ROOT/'assets/public-profile.js').read_text()
        for forbidden in ['fetch(', 'sendBeacon', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'innerHTML', 'execCommand', 'window.open', 'umami.']:
            self.assertNotIn(forbidden,js)
        self.assertIn("button.addEventListener('click'",js)
        self.assertIn('navigator.clipboard.writeText(text)',js)
        self.assertIn('range.selectNodeContents(target)',js)
        self.assertLess(len(js),3000)

    def test_invalid_bios_are_rejected(self):
        for value in ['',None,' padded','multiline\nvalue','<script>bad</script>','x'*2001]:
            site=deepcopy(self.site);site['bio_short']=value
            with self.subTest(value=value),self.assertRaises(ValueError):public_profile.exports(site)

    def test_bundle_preserves_source_text_and_order(self):
        content=self.outputs[core_styles.OUTPUT]
        parts=[]
        for path in core_styles.SOURCES:
            parts.append('/* Source: '+path+' */\n'+(ROOT/path).read_text()+'\n')
        self.assertEqual(content, '/* Generated by _scripts/core_styles.py; edit the source files. */\n'+'\n'.join(parts))
        self.assertEqual((ROOT/core_styles.OUTPUT).read_text(),content)
        for page in build.public_pages():
            links=Links(self.outputs[build.output_path(page['path'])]).links
            hrefs=[a['href'] for a in links if a.get('rel')=='stylesheet']
            self.assertEqual(hrefs.count(core_styles.href(content)),1)
            for source in core_styles.SOURCES:
                self.assertFalse(any(h.startswith('/'+source+'?') for h in hrefs))
            # Same font-provider settings and preconnections as before.
            self.assertRegex(hrefs[0], r'^/assets/site-fonts[.]css[?]v=[0-9a-f]{12}$')

    def test_every_source_changes_bundle_version_and_unsafe_css_fails(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);(root/'assets').mkdir()
            for path in core_styles.SOURCES:(root/path).write_text((ROOT/path).read_text())
            before=core_styles.href(core_styles.bundle(root))
            for path in core_styles.SOURCES:
                original=(root/path).read_text();(root/path).write_text(original+'\nbody { color: inherit; }')
                self.assertNotEqual(core_styles.href(core_styles.bundle(root)),before)
                (root/path).write_text(original)
            for bad in ['@import "x.css";', '@charset "utf-8";', '@namespace svg "http://www.w3.org/2000/svg";', 'a { background:url(image.png); }']:
                (root/'styles.css').write_text(bad)
                with self.assertRaises(ValueError):core_styles.bundle(root)

    def test_missing_duplicate_reordered_or_conditional_links_rejected(self):
        links=['<link rel="stylesheet" href="/'+p+'?v=old">' for p in core_styles.SOURCES]
        original='BEFORE\n'+'\n'.join(links)+'\nAFTER'
        result=core_styles.collapse(original,'/assets/site-core.css?v=test')
        self.assertEqual(result,'BEFORE\n<link rel="stylesheet" href="/assets/site-core.css?v=test">\nAFTER')
        bads=[links[0],''.join(links[::-1]),''.join(links+links[:1]),'<!--between-->'.join(links),original.replace('stylesheet" href','stylesheet" media="print" href',1)]
        for bad in bads:
            with self.subTest(bad=bad),self.assertRaises(ValueError):core_styles.collapse(bad,'/assets/site-core.css?v=test')

    def test_live_targets_cover_each_added_public_file(self):
        targets=check_live.targets()
        for path in [core_styles.OUTPUT,Path('assets/public-profile.js'),Path('assets/public-profile.css'),*public_profile.EXPORTS.values()]:
            self.assertEqual(targets['/'+path.as_posix()],(200,(ROOT/path).read_bytes()))

    def test_readable_bio_is_not_a_new_article_or_feed_record(self):
        for path in ['feed.xml','writing.xml','technology/feed.xml','living-well/feed.xml','poker/feed.xml']:
            self.assertNotIn('/bio/',self.outputs[Path(path)])
        p=next(p for p in build.public_pages() if p['id']=='bio')
        self.assertEqual(visibility_discovery_history.pages([p])[0]['updated'],'2026-10-17')
        self.assertEqual(p['title'],'A brief introduction.')
        self.assertIn('Nolan Kido',p['seo_title'])
        self.assertIn('Introductions',p['seo_title'])

if __name__=='__main__':unittest.main(verbosity=2)
