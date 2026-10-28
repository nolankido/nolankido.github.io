"""The study inquiry prefill is bounded, editable, and never consent."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
import unittest

import study_inquiry_history as history
import regional_link_history as subsequent_changes

ROOT=Path(__file__).resolve().parents[1]

class Elements(HTMLParser):
    def __init__(self,source):
        super().__init__(convert_charrefs=True)
        self.nodes=[]
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        self.nodes.append((tag,dict(attrs)))

class StudyInquiryTests(unittest.TestCase):
    def test_exact_five_files_restore_published_parent(self):
        self.assertEqual(set(history.change()['paths']),history.PATHS)
        for name,item in history.change()['paths'].items():
            with self.subTest(name=name):
                current=subsequent_changes.before(name,(ROOT/name).read_bytes())
                self.assertEqual(sha256(current).hexdigest(),item['new_sha256'])
                previous=history.before(name,current)
                self.assertEqual(sha256(previous).hexdigest(),item['old_sha256'])
                self.assertEqual(history.before(Path(name),current.decode()).encode(),previous)
                self.assertEqual(history.before(name,previous),previous)

    def test_unknown_changes_and_corrupt_edits_fail_closed(self):
        for name in history.PATHS:
            latest=(ROOT/name).read_bytes()
            current=subsequent_changes.before(name,latest)
            for candidate in (latest,current):
                for altered in (candidate+b'!',b'!'+candidate,candidate[1:]):
                    self.assertEqual(history.before(name,altered),altered)
            for field,value in [('old_sha256','0'*64),('new_sha256','0'*64)]:
                bad=deepcopy(history.change())
                bad['paths'][name][field]=value
                with self.subTest(name=name,field=field),patch.object(history,'change',return_value=bad):
                    if field=='old_sha256':
                        with self.assertRaises(ValueError):history.before(name,current)
                    else:
                        self.assertEqual(history.before(name,current),current)
            bad=deepcopy(history.change())
            bad['paths'][name]['edits'][0]['start']=-1
            with patch.object(history,'change',return_value=bad),self.assertRaises(ValueError):
                history.before(name,current)
        self.assertEqual(history.before('unknown.html',b'unchanged'),b'unchanged')

    def test_single_authored_start_here_contact_route_and_no_new_form(self):
        source=(ROOT/'_source/start-here.html').read_text()
        published=(ROOT/'start-here/index.html').read_text()
        target='<a href="/contact/#study-inquiry">use the existing contact form</a>'
        self.assertEqual(source.count(target),1)
        self.assertEqual(published.count(target),1)
        self.assertIn('Nothing is sent automatically.',source)
        self.assertIn('An inquiry is not consent',source)
        self.assertIn('When scripts work, the optional context field starts with',source)
        self.assertIn('You may decline a topic, skip a task, or stop.',source)
        self.assertNotIn('<form',source)
        self.assertNotIn('<input',source)
        self.assertNotIn('type="application/ld+json"',source)
        self.assertNotIn('data-website-id',source)
        before=history.before('_source/start-here.html',source)
        self.assertIn('href="/contact/#contact-form"',before)
        self.assertNotIn('href="/contact/#study-inquiry"',before)

    def test_contact_notice_is_hidden_by_default_and_describes_consent_limits(self):
        source=(ROOT/'_source/contact.html').read_text()
        page=(ROOT/'contact/index.html').read_text()
        self.assertEqual(source.count('id="study-inquiry"'),1)
        self.assertEqual(page.count('id="study-inquiry"'),1)
        notice=next(a for tag,a in Elements(page).nodes if a.get('id')=='study-inquiry')
        self.assertIn('hidden',notice)
        self.assertEqual(notice['class'],'small-copy')
        for phrase in ('Sending this form expresses interest only',
                       'it does not enroll you',
                       'authorize recording',
                       'research consent',
                       'Study details, notes, withdrawal, and deletion arrangements'):
            self.assertIn(phrase,page)
        old=history.before('contact/index.html',page)
        types={'form','input','select','option','textarea','button'}
        controls=lambda s:[(t,a) for t,a in Elements(s).nodes if t in types]
        self.assertEqual(controls(old),controls(page))
        self.assertIn('action="https://submit-form.com/uPlTgRTAR"',page)
        self.assertIn('href="/privacy/"',page)
        self.assertNotIn('type="checkbox" name="study',page)

    def test_script_only_uses_exact_public_fragment_and_blank_user_fields(self):
        script=(ROOT/'assets/contact.js').read_text()
        begin=script.index("  // An exact authored fragment offers only a fixed")
        end=script.index('  form.noValidate = true;',begin)
        block=script[begin:end]
        for exact in ["sourceHash === '#study-inquiry'","const topic = 'Website usability study'",
                      "!context.value","!message.value","context.maxLength >= topic.length",
                      "notice.hidden = false","context.value = topic",
                      "context.setAttribute('aria-describedby', 'study-inquiry')",
                      "message.setAttribute('aria-describedby', 'study-inquiry')"]:
            self.assertIn(exact,block)
        for prohibited in ('fetch(', 'sendBeacon(', 'localStorage','sessionStorage',
                           'FormData', 'submit(', 'requestSubmit(', 'addEventListener(',
                           'location.search', 'document.referrer', 'innerHTML',
                           'dispatchEvent(', 'consent = true'):
            self.assertNotIn(prohibited,block)
        self.assertEqual(script.count("sourceHash === '#study-inquiry'"),1)
        self.assertIn("if (/^#report-[a-z0-9-]{1,64}$/.test(sourceHash))",script)
        self.assertNotIn("sourceHash === '#study-inquiry'",history.before('assets/contact.js',script))

    def test_contact_script_cache_tracks_exact_downloaded_bytes(self):
        script=(ROOT/'assets/contact.js').read_bytes()
        page=(ROOT/'contact/index.html').read_text()
        token='/assets/contact.js?v='+sha256(script).hexdigest()[:12]
        self.assertEqual(page.count(token),1)
        self.assertNotIn('consent has been granted',page)
        self.assertNotIn('You are enrolled',page)
        for route in ('/contact/','/privacy/'):
            self.assertIn('href="'+route+'"',(ROOT/'start-here/index.html').read_text())

if __name__=='__main__':
    unittest.main()
