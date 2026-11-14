#!/usr/bin/env python3
"""Run website release checks locally without any CI or network actions."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def forbid_workflows() -> None:
    folder = ROOT / '.github' / 'workflows'
    active = sorted(p for p in folder.glob('*') if p.is_file() and p.suffix.lower() in {'.yml', '.yaml'})
    if active:
        raise RuntimeError('GitHub Actions are prohibited for this site: ' + ', '.join(str(p.relative_to(ROOT)) for p in active))


def check(label: str, args: list[str]) -> bool:
    print(f'\n=== {label} ===', flush=True)
    if '-s' in args and '-p' in args:
        folder = ROOT / args[args.index('-s') + 1]
        pattern = args[args.index('-p') + 1]
        if not any(folder.glob(pattern)):
            print(f'{label}: FAIL (no tests match {pattern})', flush=True)
            return False
    result = subprocess.run([sys.executable, *args], cwd=ROOT, check=False)
    print(f'{label}: {"PASS" if result.returncode == 0 else "FAIL"}', flush=True)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Also run historical units in per-module bounded processes (can take time)')
    parser.add_argument('--browser', action='store_true', help='Also run local browser scripts; requires Playwright and browsers')
    args = parser.parse_args()
    try:
        forbid_workflows()
    except RuntimeError as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        return 2

    tasks = [
        ('Deterministic build', ['_scripts/build.py', '--check']),
        ('Player profile build', ['_scripts/build_player_profile.py', '--check']),
        ('Portland video companion build', ['_scripts/build_poker_episode.py', '--check']),
        ('Stand Off video companion build', ['_scripts/build_standoff_episode.py', '--check']),
        ('Local laptop guide build', ['_scripts/build_local_laptop_case.py', '--check']),
        ('Independent reply audit build', ['_scripts/build_reply_audit_case.py', '--check']),
        ('Independent reply audit contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_reply_audit_case.py', '-q']),
        ('Local laptop article and loopback contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_local_laptop_case.py', '-q']),
        ('Portland video companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_portland_episode.py', '-q']),
        ('Stand Off video companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn33_standoff_companion.py', '-q']),
        ('Release integrity regressions', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn34_release_integrity.py', '-q']),
        ('AI and poker evidence article', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn35_ai_poker_case.py', '-q']),
        ('About reader navigation and proof', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn36_about_reader.py', '-q']),
        ('Public internal links and fragments', ['_scripts/check_internal_links.py']),
        ('Internal link negative controls', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn37_internal_links.py', '-q']),
        ('Homepage evidence and provenance', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn38_home_proof.py', '-q']),
        ('Homepage evidence shortcut', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn39_home_shortcut.py', '-q']),
        ('Homepage practical first choice', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn99_home_useful_first.py', '-q']),
        ('Resources hub: discoverable original kits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_resources_hands_on_kits.py', '-q']),
        ('Evidence-linked public project portfolio', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_public_project_portfolio.py', '-q']),
        ('Public RightsReceipt source-backed licensing case', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_rightsreceipt_public_case.py', '-q']),
        ('Published accounting research authorship and findings', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_published_accounting_research.py', '-q']),
        ('Source-linked public biography and fact guide', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_profile_public_fact_guide.py', '-q']),
        ('Source-linked wine tasting guide and blank worksheet', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_wine_tasting_notes.py', '-q']),
        ('Original incremental game lab, upgrade logic and playtest protocol', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_incremental_game_loop.py', '-q']),
        ('AI answer citation panel offline checker and synthetic controls', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_ai_citation_panel.py', '-q']),
        ('Incremental upgrade payback calculator and source-linked teaching guide', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_incremental_upgrade_payback.py', '-q']),
        ('Reproducible AI business workflow pilot and offline audit', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_ai_workflow_pilot.py', '-q']),
        ('Homepage mobile practical shortcut', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn100_mobile_start_shortcut.py', '-q']),
        ('AI task brief one-click quick start', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn101_brief_quick_start.py', '-q']),
        ('AI task brief example opening focus', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn102_brief_opening_focus.py', '-q']),
        ('AI task brief assembled preview handoff', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn103_brief_result_handoff.py', '-q']),
        ('AI task brief reviewed-preview export route', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn104_brief_review_to_export.py', '-q']),
        ('AI task brief visible manual selection', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn105_brief_selection_visibility.py', '-q']),
        ('AI task brief selection starts at first line', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn106_brief_selection_start.py', '-q']),
        ('AI task brief truthful export outcomes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn107_brief_export_outcomes.py', '-q']),
        ('AI task brief visible copy instruction', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn108_brief_visible_copy_cue.py', '-q']),
        ('AI task brief readable and accessible manual copy', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn109_brief_copy_accessibility.py', '-q']),
        ('AI task brief extreme reflow navigation', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn110_brief_extreme_reflow.py', '-q']),
        ('AI task brief manual native-copy command', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn111_brief_manual_copy_command.py', '-q']),
        ('AI task brief incomplete-selection warning', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn112_brief_partial_selection.py', '-q']),
        ('AI task brief keyboard and touch copy guidance', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn114_brief_copy_shortcuts.py', '-q']),
        ('AI task brief nearby export alternatives', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn115_brief_export_alternatives.py', '-q']),
        ('AI task brief short viewport export handoff', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn116_brief_short_viewport.py', '-q']),
        ('AI task brief enlarged-text answer-check handoff', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn117_brief_enlarged_handoff.py', '-q']),
        ('AI task brief visible fallback copy guidance', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn118_brief_visible_fallback_copy.py', '-q']),
        ('AI task brief native copy and partial selection state', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn119_brief_selection_state.py', '-q']),
        ('AI task brief exhausted export recovery', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn120_brief_dual_export_failure.py', '-q']),
        ('AI task brief honest unconfirmed text selection', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn121_brief_unconfirmed_selection.py', '-q']),
        ('AI task brief keyboard focus-loss copy guidance', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn122_brief_focus_loss.py', '-q']),
        ('Homepage significant-change freshness', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn47_home_freshness.py', '-q']),
        ('Free Search Console checker synthetic visitor demo', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn48_visibility_demo.py', '-q']),
        ('Current public poker video discovery', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn40_poker_videos.py', '-q']),
        ('NolanPoker channel visitor route', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn41_channel_route.py', '-q']),
        ('Public website-visibility case and source limits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn42_site_visibility_case.py', '-q']),
        ('Website case migration and preserved reader routes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn51_visibility_article.py', '-q']),
        ('Reciprocal website case reader paths', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn123_website_case_links.py', '-q']),
        ('Technology hub direct case routes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn124_technology_case_routes.py', '-q']),
        ('Primary identity tagline and search previews', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn125_primary_brand_language.py', '-q']),
        ('Practical AI articles explain the canonical method', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn126_article_method_links.py', '-q']),
        ('Standalone AI cases summarize evidence and limits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn127_evidence_snapshots.py', '-q']),
        ('Standalone AI cases show bounded evidence before long prose', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn128_early_evidence.py', '-q']),
        ('Mobile evidence summaries have native hero shortcuts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn129_mobile_evidence_jumps.py', '-q']),
        ('Missing links recover to public routes without guessing', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn130_404_recovery.py', '-q']),
        ('Explicit topic acronyms find the matching public articles', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn131_find_acronyms.py', '-q']),
        ('Public AI cases link their author to bounded evidence', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn132_case_author_context.py', '-q']),
        ('About evidence arrives on verifiable work with visible target', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn133_about_evidence_arrival.py', '-q']),
        ('Public wine and game interests have honest, private-safe entrypoints', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn134_hobby_identity_bridge.py', '-q']),
        ('About profile menu reaches all six sections on desktop and mobile', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn135_about_hobby_navigation.py', '-q']),
        ('Homepage proof and practical AI native arrivals visibly identify targets', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn136_home_ai_arrivals.py', '-q']),
        ('Homepage AI proof links directly to the source-backed project example', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn137_home_project_evidence.py', '-q']),
        ('Anchored Review Reply Writer sections visibly identify the arrival', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn138_project_fragment_arrivals.py', '-q']),
        ('Mobile project evidence shortcuts remain labeled and tappable', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn143_project_shortcuts.py', '-q']),
        ('Scrollable evidence tables explain touch and keyboard navigation', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn144_table_scroll_guidance.py', '-q']),
        ('Review Reply Writer evidence routes to method and limits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn145_reply_evidence_paths.py', '-q']),
        ('Technology hub evidence tables explain sideways reading', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn146_technology_hub_table_hints.py', '-q']),
        ('All Technology evidence tables explain sideways reading', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn147_remaining_table_hints.py', '-q']),
        ('Public South Point video links and provenance boundaries', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn148_south_point_video.py', '-q']),
        ('Mobile-first NolanPoker gallery and retained source notes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn149_nolanpoker_gallery.py', '-q']),
        ('Local NolanPoker thumbnails and checked public titles', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn150_nolanpoker_thumbnails.py', '-q']),
        ('Two narrated real hand records', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_real_portland_hands.py', '-q']),
        ('Public Poker and combined RSS receipts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_manual_poker_feed.py', '-q']),
        ('Player sitemap and live-target contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_sitemap.py', '-q']),
        ('Player Find index contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_find.py', '-q']),
        ('Standalone Find section contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_standalone_search_sections.py', '-q']),
        ('Standalone reader arrival contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_standalone_reader_arrivals.py', '-q']),
        ('Public profile and topical search', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_site_find.py', '-q']),
        ('Complete author archive and standalone articles', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_author_archive_standalone.py', '-q']),
        ('SEO and metadata', ['_scripts/check_search.py']),
        ('HTML5 parsing including standalone pages', ['_tests/check_html5.py']),
    ]
    if args.full:
        tasks.extend([
            ('Full historical unit suite (bounded)', [
                '_scripts/check_historical_batches.py', '--all', '--timeout-seconds', '90']),
        ])
    else:
        tasks.append(('Poker evidence regressions', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_visibility_poker_player*.py', '-q']))
    if args.browser:
        suites = sorted((ROOT / '_tests').glob('*_browser.py'))
        standalone = ROOT / '_tests' / 'browser.py'
        if standalone.is_file():
            suites.insert(0, standalone)
        tasks.extend((f'Local browser: {p.stem}', [str(p.relative_to(ROOT))]) for p in suites)
    results = [(label, check(label, command)) for label, command in tasks]
    count = sum(passed for _, passed in results)
    print(f'\nLocal release checks: {count}/{len(tasks)} passed. No GitHub Actions were invoked.')
    failures = [label for label, passed in results if not passed]
    if failures:
        print('Failed release groups: ' + ', '.join(failures))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
