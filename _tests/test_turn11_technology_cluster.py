"""Turn 11: differentiated Technology tasks and durable manual case discovery."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '_scripts'))
import audit_technology_cluster as cluster


class TechnologyClusterTurn11(unittest.TestCase):
    def test_matrix_has_unique_questions_and_contextual_neighbors(self):
        rows = cluster.load_matrix(ROOT)
        self.assertEqual(len(rows), 19)
        self.assertEqual(len(set(row['reader_question'].lower() for row in rows)), 19)
        self.assertEqual({row['task'] for row in rows}, cluster.TASKS)
        for row in rows:
            self.assertEqual(len(set(row['related_paths'].split('|'))),
                             len(row['related_paths'].split('|')))
            self.assertGreaterEqual(len(row['related_paths'].split('|')), 2)
            self.assertLessEqual(len(row['related_paths'].split('|')), 3)

    def test_eight_task_routes_cover_every_flagship(self):
        built = (ROOT / 'technology/index.html').read_text(encoding='utf-8')
        routes, rows = cluster.task_routes(built)
        self.assertEqual(rows, 8)
        self.assertEqual(routes, {row['route'] for row in cluster.load_matrix(ROOT)} - {'/technology/'})

    def test_find_feed_sitemap_canonicals_and_contextual_routes(self):
        report = cluster.audit(ROOT)
        self.assertEqual(report['issues'], [], '\n'.join(report['issues']))
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['technology_routes'], 19)
        self.assertEqual(report['technology_article_feed_items'], 16)

    def test_both_standalone_builders_retain_their_own_sources(self):
        for builder in ('build_local_laptop_case.py', 'build_reply_audit_case.py'):
            with self.subTest(builder=builder):
                result = subprocess.run([sys.executable, str(ROOT / '_scripts' / builder), '--check'],
                                        cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_canonical_parser_finds_duplicate_and_missing_values(self):
        right = '<link rel="canonical" href="https://nolankido.com/technology/task-brief/">'
        self.assertEqual(cluster.canonical_urls(right), ['https://nolankido.com/technology/task-brief/'])
        self.assertEqual(len(cluster.canonical_urls(right + right)), 2)
        self.assertEqual(cluster.canonical_urls('<link rel="alternate" href="/technology/feed.xml">'), [])

    def test_find_parser_ignores_generic_navigation(self):
        sample = '<a href="/technology/">Navigation</a><li class="find-item" data-kind="guide"><p>Guide</p><h3><a href="/technology/check-ai-answers/">Check answers</a></h3></li>'
        self.assertEqual(cluster.find_routes(sample), ['/technology/check-ai-answers/'])


if __name__ == '__main__':
    unittest.main()
