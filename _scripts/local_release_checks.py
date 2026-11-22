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
        ('Book pages source/output build', ['_scripts/build_books.py', '--check']),
        ('Player profile build', ['_scripts/build_player_profile.py', '--check']),
        ('Portland video companion build', ['_scripts/build_poker_episode.py', '--check']),
        ('Stand Off video companion build', ['_scripts/build_standoff_episode.py', '--check']),
        ('Reserve Day 1 video companion build', ['_scripts/build_reserve_day1_episode.py', '--check']),
        ('Local laptop guide build', ['_scripts/build_local_laptop_case.py', '--check']),
        ('Independent reply audit build', ['_scripts/build_reply_audit_case.py', '--check']),
        ('Independent reply audit contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_reply_audit_case.py', '-q']),
        ('Local laptop article and loopback contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_local_laptop_case.py', '-q']),
        ('Portland video companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_portland_episode.py', '-q']),
        ('Stand Off video companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn33_standoff_companion.py', '-q']),
        ('Reserve Day 1 companion contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn13_reserve_companion.py', '-q']),
        ('Reserve video listing offline agreement', ['_scripts/check_reserve_video_listing.py']),
        ('Reserve video listing drift negative controls', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn14_reserve_listing_alignment.py', '-q']),
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
        ('Turn 44 RightsReceipt local software proof and acceptance boundary', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn44_rightsreceipt_software_proof.py', '-q']),
        ('Turn 45 project hub routes to pinned RightsReceipt evidence', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn45_project_proof_navigation.py', '-q']),
        ('Turn 45 Review Reply Writer owner decisions and synthetic checker misses', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn45_reply_owner_decision_lab.py', '-q']),
        ('Turn 46 four-case AI stop rules, human authority and private worksheet', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn46_ai_stop_rules.py', '-q']),
        ('Published accounting research authorship and findings', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_published_accounting_research.py', '-q']),
        ('Source-linked public biography and fact guide', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_profile_public_fact_guide.py', '-q']),
        ('Source-linked wine tasting guide and blank worksheet', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_wine_tasting_notes.py', '-q']),
        ('Original incremental game lab, upgrade logic and playtest protocol', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_incremental_game_loop.py', '-q']),
        ('AI answer citation panel offline checker and synthetic controls', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_ai_citation_panel.py', '-q']),
        ('Turn 40: frozen 25-prompt mode roster and exact question evidence', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn40_frozen_observation_integrity.py', '-q']),
        ('AI citation guide discoverability in local site search', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_ai_citation_find_discovery.py', '-q']),
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
        ('NolanPoker first-video choice and accessible card arrivals', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn151_nolanpoker_choices.py', '-q']),
        ('Poker short-stack 3 to 20 BB reader path', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn152_short_stack_route.py', '-q']),
        ('NolanPoker real-hand to short-stack study links', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn153_poker_hand_study.py', '-q']),
        ('Reciprocal study links in both Portland companion pages', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn154_companion_study_routes.py', '-q']),
        ('Real-hand reading links inside 6–10 and 10–20 BB guides', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn155_real_hand_guides.py', '-q']),
        ('Outcome-independent questions in both tournament companions', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn156_hand_review_exercises.py', '-q']),
        ('Responsive hand-review answers and direct lesson links', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn157_hand_review_accessibility.py', '-q']),
        ('Keyboard focus position and browser test contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn158_keyboard_focus.py', '-q']),
        ('In-memory responsive hand-review browser contract', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn159_content_browser.py', '-q']),
        ('Browser root provenance and installed Chromium selection', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn160_browser_provenance.py', '-q']),
        ('Three verified tournament hands in the hand-review method', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn161_hand_review_routes.py', '-q']),
        ('Annotated two-decision A-K review and upgraded private worksheet', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn162_two_decision_review.py', '-q']),
        ('Source-limited 6-4 bubble shove review and ICM uncertainty', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn163_64o_bubble_review.py', '-q']),
        ('Four-handed pocket sevens and separate opening/calling ranges', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn164_sevens_review.py', '-q']),
        ('Cross-review accuracy and Stand Off survivor payout context', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn165_worked_review_consistency.py', '-q']),
        ('Unseen fictional review case and separate objective checking key', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn166_outcome_blind_practice.py', '-q']),
        ('Mobile readable poker practice and separate checking key', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn167_mobile_practice_readers.py', '-q']),
        ('Matched practice step anchors and review return links', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn168_practice_anchor_journeys.py', '-q']),
        ('Two narrated real hand records', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_real_portland_hands.py', '-q']),
        ('Public Poker and combined RSS receipts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_manual_poker_feed.py', '-q']),
        ('Player sitemap and live-target contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_sitemap.py', '-q']),
        ('Player Find index contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_player_find.py', '-q']),
        ('Standalone Find section contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_standalone_search_sections.py', '-q']),
        ('Standalone reader arrival contracts', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_standalone_reader_arrivals.py', '-q']),
        ('Public profile and topical search', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_site_find.py', '-q']),
        ('Complete author archive and standalone articles', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_author_archive_standalone.py', '-q']),
        ('Standalone book publication and release coverage', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_book_pages.py', '-q']),
        ('Turn 48 book reader routes, native exercises and narrow-screen keyboard support', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn48_book_reader_journeys.py', '-q']),
        ('Turn 49 topic-to-book exercises and reciprocal free-guide paths', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn49_topic_book_paths.py', '-q']),
        ('Turn 50 first-screen practical AI proof and task routes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn50_first_screen_identity.py', '-q']),
        ('Turn 51 practical AI topic ownership and guide-to-calculator distinction', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn51_topic_ownership.py', '-q']),
        ('Turn 52 standalone 10 BB ICM audit and sitemap registration', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn52_10bb_playbook.py', '-q']),
        ('Turn 65 10 BB site Find reader discovery and section routes', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn65_tenbb_find.py', '-q']),
        ('Turn 66 playbook contextual reader paths', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn66_tenbb_reader_paths.py', '-q']),
        ('Turn 67 standalone written Playbook status and section navigation', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn67_playbook_standalone.py', '-q']),
        ('Turn 68 practical AI workflow pilot discovery from Home and Start Here', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn68_workflow_pilot_discovery.py', '-q']),
        ('Turn 69 recorded AI source-check crosslinks and evidence limits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn69_ai_source_case_links.py', '-q']),
        ('Turn 49 catalog choice-to-practice handoff and Home overview deduplication', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn49_book_catalog_handoff.py', '-q']),
        ('Turn 47: unknown-versus-verified book edition provenance and ISBN/ASIN safety', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn47_book_edition_evidence.py', '-q']),
        ('SEO, metadata and snapshot parity', ['_scripts/check_search.py', '--verify-snapshot', '_reports/search-audit.json']),
        ('SEO snapshot drift negative controls', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_search_audit_snapshot.py', '-q']),
        ('Private GSC/Bing/Umami scorecard evidence and zero/null safety', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_visibility_private_scorecard.py', '-q']),
        ('Turn 41 evidence-prioritized canonical routes and beginner prerequisites', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn41_evidence_opportunities.py', '-q']),
        ('Turn 42 source-backed website repair proof path', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn42_repair_proof_path.py', '-q']),
        ('Turn 43 published content receipt and video approval limits', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn43_published_content_receipt.py', '-q']),
        ('Turn 53 real published companion revision and open audiovisual QA', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn53_poker_published_revision.py', '-q']),
        ('Turn 54 featured NolanPoker public video-title and companion link agreement', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn54_nolanpoker_listing_accuracy.py', '-q']),
        ('Turn 55 featured video to source-limited question and fictional practice', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn55_video_to_practice.py', '-q']),
        ('Turn 56 official TDA 2026 short all-in reopen scope and player history', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn56_tda_reopening.py', '-q']),
        ('Turn 57 independent three-player ICM and payout sensitivity', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn57_icm_prize_audit.py', '-q']),
        ('Turn 58 cutoff shove versus big blind call price and omitted actions', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn58_shove_branch.py', '-q']),
        ('Turn 59 personal cash versus fictional payout ladder and quiz', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn59_payout_consistency.py', '-q']),
        ('Turn 60 complete card-filtered Bayes range update, exact source and blocker checks', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn60_bayes_update.py', '-q']),
        ('Live diagnostic result classification and priority scope', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn38_live_evidence.py', '-q']),
        ('Turn 62 10 BB HTML5 publication coverage and fail-closed guards', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn62_html5_tenbb.py', '-q']),
        ('Turn 63 public noindex HTML download safety', ['-m', 'unittest', 'discover', '-s', '_tests', '-p', 'test_turn63_public_html_downloads.py', '-q']),
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
