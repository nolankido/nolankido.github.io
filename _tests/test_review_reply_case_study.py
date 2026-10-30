"""Publication assertions for the October 29 Review Reply Writer evidence update.

These checks protect the exact source/output pair and verify that the study
does not turn offline template results into AI success claims. Older release
provenance stays independently checkable through a SHA-gated successor.
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_tests'))
import visibility_discovery_history as history

SOURCE = '_source/technology/local-ai-review-replies.html'
OUTPUT = 'technology/local-ai-review-replies/index.html'
FINDER = 'find/index.html'
EXTRA_ANCHORS = (
    'reply-evaluation',
    'reply-evaluation-results',
    'reply-evaluation-lessons',
    'reply-evaluation-gemma',
    'reply-evaluation-method',
    'reply-evaluation-limits',
)


class ReviewReplyCaseStudyTests(unittest.TestCase):
    def test_study_is_in_editable_source_and_committed_page(self):
        source = (ROOT / SOURCE).read_text(encoding='utf-8')
        html = (ROOT / OUTPUT).read_text(encoding='utf-8')
        self.assertIn(source, html)
        self.assertEqual(source.count('Review Reply Writer extended evidence review: start'), 1)
        self.assertEqual(source.count('Review Reply Writer extended evidence review: end'), 1)
        self.assertEqual(html.count('class="reader-outline-count">12 sections'), 1)
        self.assertIn('About 11 min read', html)
        for anchor in EXTRA_ANCHORS:
            self.assertEqual(source.count('id="' + anchor + '"'), 1)
            self.assertIn('href="#' + anchor + '"', html)
        self.assertIn('rel="canonical" href="https://nolankido.com/technology/local-ai-review-replies/"', html)
        self.assertIn('content="2026-10-27"', html)
        finder = (ROOT / FINDER).read_text(encoding='utf-8')
        self.assertEqual(finder.count('"local-ai-review-replies/":'), 1)
        for anchor in EXTRA_ANCHORS:
            self.assertIn('"' + anchor + '"', finder)


    def test_claims_distinguish_template_study_from_old_model_runs(self):
        source = (ROOT / SOURCE).read_text(encoding='utf-8')
        for required in (
            '29 non-AI template drafts', 'Actual model calls', '0',
            'Human owner assessments', 'What the archived Gemma tests actually showed.',
            'not a controlled ranking of engines', 'no head-to-head 30-case current-source Gemma comparison',
            'AI Works Human Decides', 'The 30-case run returned 29 templates and blocked one.',
            'not a 96.7% safety rate',
        ):
            self.assertIn(required.lower(), source.lower())
        for filename in (
            'template-full-2026-10-29.json',
            'live-smoke-2026-10-13.json',
            'live-quality-smoke-2026-10-13.json',
            'CASE_STUDY_EVIDENCE_2026_10_29.md',
        ):
            self.assertIn(filename, source)
        self.assertNotIn('\u2014', source)

    def test_older_publication_restores_only_exact_reviewed_blobs(self):
        for path in (SOURCE, OUTPUT, FINDER):
            current = (ROOT / path).read_bytes()
            restored = history.before(path, current)
            self.assertNotEqual(current, restored, path)
            self.assertEqual(history._blob_sha(current), history.STUDY_NEW_BLOBS[path])
            self.assertEqual(history._blob_sha(restored), history.STUDY_OLD_BLOBS[path])
            self.assertEqual(history.before(path, restored), restored)
            mutated = current + b'UNREVIEWED'
            self.assertEqual(history.before(path, mutated), mutated)


if __name__ == '__main__':
    unittest.main()
