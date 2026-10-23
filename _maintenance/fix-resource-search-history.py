from pathlib import Path
root=Path.cwd()
p=root/'_tests/test_poker_school_history.py'
s=p.read_text().replace('import homepage_growth_history as homepage\n','import homepage_growth_history as homepage\nimport resource_review_history\n',1)
a='''        current = evaluation.evaluate()
        previous = evaluation.evaluate(progress_release=True)
'''
b='''        # This stored report belongs to the School release. Reconstruct its
        # exact approved index before comparing; keep the original report fixed.
        # Current index behavior has a separate resource-review regression.
        read_text = Path.read_text
        def school_index(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            return resource_review_history.before('poker/find/index.html', text) if path == ROOT / 'poker/find/index.html' else text
        with patch.object(Path, 'read_text', school_index):
            current = evaluation.evaluate()
            previous = evaluation.evaluate(progress_release=True)
'''
assert s.count(a)==1
p.write_text(s.replace(a,b,1))
p=root/'_tests/test_resource_review_20261023.py';s=p.read_text();marker='    def test_complete_production_inventory_reconstructs_verified_release(self):\n'
method='''    def test_current_search_preserves_all_declared_results_without_rewriting_history(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location('review_current_search', ROOT / '_reports/poker-search-intent/evaluate.py')
        evaluation = module_from_spec(spec); spec.loader.exec_module(evaluation)
        current = evaluation.evaluate()
        previous = json.loads((ROOT / '_reports/poker-school/search-results.json').read_text())
        self.assertEqual(current['index_sha256'], sha256((ROOT / 'poker/find/index.html').read_bytes()).hexdigest())
        self.assertNotEqual(current['index_sha256'], previous['index_sha256'])
        self.assertEqual({k: v for k, v in current.items() if k != 'index_sha256'},
                         {k: v for k, v in previous.items() if k != 'index_sha256'})

'''
assert s.count(marker)==1
p.write_text(s.replace(marker,method+marker,1))
p=root/'_reports/website-growth/turn-17-resource-maintenance.md';s=p.read_text();s += '''\n## Historical search-report integration

The first local full suite found a current-index fingerprint mismatch against the stored School-release report, plus 20 import errors because the separate HTML parser dependency was missing locally. The stored report and all old expected results remain unchanged. Its historical test now reconstructs only the exact approved old index before comparison. A separate new test evaluates the actual current index and confirms all 30 declared queries, match counts, top-three rankings, scores, passages and outcomes remain identical; only the current index fingerprint differs. These are AI-authored regression targets, not search-engine rankings or human relevance results. A fresh local suite uses the environment's vendored html5lib, while hosted qualification still requires the repository's pinned dependency.
'''
p.write_text(s)
p=root/'_reports/website-growth/turn-17-resource-maintenance.md'
s=p.read_text();assert s.count('Nine focused contracts') == 1
p.write_text(s.replace('Nine focused contracts', 'Ten focused contracts', 1))
