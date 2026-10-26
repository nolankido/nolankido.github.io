"""Opt-in visitor-study interest without new collection or implied consent."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
import re
import unittest
import study_interest_history as history

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = '_source/start-here.html'
PUBLIC = 'start-here/index.html'
MARK = 'id="study-interest"'
TARGET = '/contact/#contact-form'

class ElementParser(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.nodes.append((tag,dict(attrs)))

class StudyInterestTests(unittest.TestCase):
    def test_full_file_history_is_exact_and_idempotent(self):
        self.assertEqual(set(history.change()['paths']), history.PATHS)
        for name,item in history.change()['paths'].items():
            with self.subTest(name=name):
                raw=(ROOT/name).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(),item['new_sha256'])
                previous=history.before(name,raw)
                self.assertEqual(sha256(previous).hexdigest(),item['old_sha256'])
                self.assertEqual(history.before(Path(name),raw.decode()).encode(),previous)
                self.assertEqual(history.before(name,previous),previous)

    def test_unknown_and_corrupt_history_cannot_mask_changes(self):
        for name in history.PATHS:
            raw=(ROOT/name).read_bytes()
            for unexpected in (raw+b'!',b'!'+raw,raw[1:]):
                self.assertEqual(history.before(name,unexpected),unexpected)
            bad=deepcopy(history.change())
            bad['paths'][name]['old_sha256']='0'*64
            with patch.object(history,'change',return_value=bad),self.assertRaises(ValueError):
                history.before(name,raw)
            bad=deepcopy(history.change())
            bad['paths'][name]['new']='wrong literal text'
            with patch.object(history,'change',return_value=bad),self.assertRaises(ValueError):
                history.before(name,raw)
        self.assertEqual(history.before('index.html',b'unrelated'),b'unrelated')

    def test_single_static_invitation_is_source_identical_and_accessible(self):
        source=(ROOT/ORIGIN).read_text()
        page=(ROOT/PUBLIC).read_text()
        block=re.search(r'<section id="study-interest".*?</section>',source,re.S)
        self.assertIsNotNone(block)
        self.assertEqual(source.count(MARK),1)
        self.assertEqual(page.count(MARK),1)
        self.assertIn(block.group(),page)
        invite=ElementParser(block.group()).nodes
        self.assertEqual(invite[0],('section',{'id':'study-interest','aria-labelledby':'study-interest-title'}))
        self.assertEqual([a for t,a in invite if t=='h3'],[{'id':'study-interest-title'}])
        self.assertEqual([a['href'] for t,a in invite if t=='a'],[TARGET,'/privacy/'])
        self.assertNotIn('<form',block.group())
        self.assertNotIn('<script',block.group())
        self.assertNotIn('<input',block.group())
        self.assertNotIn('name=',block.group())
        self.assertNotIn('data-',block.group())

    def test_research_offer_has_no_consent_or_outcome_claim(self):
        invitation=re.search(r'<section id="study-interest".*?</section>',(ROOT/ORIGIN).read_text(),re.S)[0]
        for phrase in ('adult new to this site','25-minute','two fictional tasks',
                       'your usual device','decline a topic','skip a task, or stop',
                       'An inquiry is not consent','withdrawal and deletion arrangements',
                       'No audio, video or screen recording is planned by default',
                       'Please do not send task answers'):
            self.assertIn(phrase,invitation)
        for claim in ('people completed','participants passed','95%','registered volunteers',
                      'book your session','consent has been given'):
            self.assertNotIn(claim,invitation)

    def test_contact_route_reuses_existing_private_boundaries(self):
        contact=(ROOT/'contact/index.html').read_text()
        p=ElementParser(contact).nodes
        forms=[a for t,a in p if t=='form']
        self.assertEqual(len(forms),1)
        self.assertEqual(forms[0]['id'],'contact-form')
        fields={a.get('name') for t,a in p if 'required' in a}
        self.assertEqual(fields,{'name','email','message'})
        self.assertIn('Turnstile', (ROOT/'_source/privacy.html').read_text())
        self.assertIn('Formspark', (ROOT/'_source/privacy.html').read_text())
        self.assertNotIn('study-interest',contact)
        self.assertIn('href="/privacy/"',(ROOT/PUBLIC).read_text())

    def test_four_task_routes_and_reader_entries_remain_unchanged(self):
        original=history.before(PUBLIC,(ROOT/PUBLIC).read_text())
        current=(ROOT/PUBLIC).read_text()
        for phrase in ('/technology/task-brief/', '/technology/check-ai-answers/',
                       '/living-well/weekly-reset/', '/poker/first-live-tournament/'):
            self.assertEqual(current.count('href="'+phrase+'"'),original.count('href="'+phrase+'"'))
        for identity in ('start-intro-title','start-tasks-title','start-routes-title','start-reading-title','reading-this-site'):
            self.assertEqual(current.count('id="'+identity+'"'),original.count('id="'+identity+'"'))
        self.assertEqual(len(re.findall(r'<script[^>]+src=',current)),len(re.findall(r'<script[^>]+src=',original)))
        self.assertEqual(len(re.findall(r'<form\b',current)),len(re.findall(r'<form\b',original)))
        self.assertEqual(len(re.findall(r'<textarea\b',current)),len(re.findall(r'<textarea\b',original)))

if __name__=='__main__':unittest.main()
