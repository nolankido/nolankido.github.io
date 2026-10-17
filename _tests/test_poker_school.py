"""Poker School offer integrity, privacy boundaries and explicit opt-in."""
from pathlib import Path
import unittest
from test_site import ROOT, Page, build


class PokerSchoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = build.public_pages()
        cls.outputs = build.build_outputs()

    def test_canonical_offer_without_false_launch_claims(self):
        page = next(p for p in self.pages if p['path'] == '/poker/school/')
        self.assertEqual(page['id'], 'poker-school')
        text = self.outputs[Path('poker/school/index.html')]
        self.assertIn('<link rel="canonical" href="https://nolankido.com/poker/school/">', text)
        self.assertIn('Poker School is in development.', text)
        self.assertIn('No payment, student account or promised coaching', text)
        self.assertIn('The free course stays free.', text)
        self.assertEqual(text.count('id="course-interest"'), 1)

    def test_form_uses_existing_provider_with_consent_and_removal(self):
        text = self.outputs[Path('poker/school/index.html')]
        page = Page(text)
        forms = [f for f in page.tags('form') if f.get('id') == 'poker-interest-form']
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0].get('action'), 'https://submit-form.com/uPlTgRTAR')
        self.assertIn('name="interest_action"', text)
        self.assertIn('value="register"', text)
        self.assertIn('value="remove"', text)
        self.assertIn('id="interest-consent" name="interest_consent" type="checkbox" value="yes" required', text)
        self.assertIn('id="contact-fields" disabled', text)
        self.assertIn('data-sitekey="0x4AAAAAAFI2X8NC1cauc_zz"', text)
        self.assertIn('/privacy/#poker-school-requests', text)
        self.assertIn('not instant mailing-list enrollment', self.outputs[Path('privacy/index.html')])
        self.assertNotIn('localStorage', (ROOT / 'assets/contact.js').read_text())

    def test_assets_and_course_entrypoints(self):
        text = self.outputs[Path('poker/school/index.html')]
        self.assertIn('/assets/poker-school.css?v=', text)
        self.assertIn('/assets/contact.js?v=', text)
        for path in ['poker/index.html', 'poker/free-poker-learning-path/index.html', 'poker/study/index.html']:
            self.assertIn('href="/poker/school/"', self.outputs[Path(path)], path)
        for path in ['poker/index.html', 'poker/study/index.html']:
            self.assertIn('href="/poker/free-poker-learning-path/"', self.outputs[Path(path)], path)

    def test_ordinary_contact_form_remains_available(self):
        form = self.outputs[Path('contact/index.html')]
        self.assertIn('id="contact-form"', form)
        self.assertIn('name="message" rows="7" required', form)
        self.assertIn("if (!pokerInterest) return originalLabel", (ROOT / 'assets/contact.js').read_text())


if __name__ == '__main__':
    unittest.main()
