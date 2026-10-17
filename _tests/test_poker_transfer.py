"""Read-only QA of the public draft transfer packet, not a learning outcome."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from contextlib import contextmanager
import shutil
import tempfile
import unittest
from unittest.mock import patch
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("poker_transfer_verify", ROOT / "_reports/poker-transfer/verify.py")
module = module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class PokerTransferTests(unittest.TestCase):
    def test_rejects_missing_lesson_exposure_counts(self):
        with self.changed_packet("summary-form.md", "Assigned lesson seen (yes / no / unsure)", "Other exposure"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_point_level_outcomes(self):
        with self.changed_packet("summary-form.md", "| S5-A | assisted |", "| S5-A | combined |"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_full_card_names(self):
        with self.changed_packet("cards/S3-A.md", "queen of clubs", "Qc"):
            with self.assertRaises(AssertionError):
                module.check()

    @contextmanager
    def changed_packet(self, filename, before, after):
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "packet"
            shutil.copytree(module.FOLDER, copied)
            target = copied / filename
            source = target.read_text()
            self.assertIn(before, source)
            target.write_text(source.replace(before, after))
            with patch.object(module, "FOLDER", copied):
                yield

    def test_rejects_card_and_source_drift(self):
        with self.changed_packet("cards/S2-B.md", "at least 30 counters each still behind", "no counters behind"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_hand_comparison_repair_in_key(self):
        with self.changed_packet("facilitator-key.md", "/poker/hand-rankings/#compare", "/poker/betting-with-a-purpose/#purpose"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_assisted_attempt_counts(self):
        with self.changed_packet("summary-form.md", "Assisted attempted (any help)", "Hint only"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_conflated_exposure_fields(self):
        with self.changed_packet("session-form.md", "Prior exposure to this case's answer key: yes / no / unsure", "Prior exposure to a similar problem or answer key: ______"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_missing_assisted_reasoning_record(self):
        with self.changed_packet("session-form.md", "Assisted reasoning point 3:", "Unscored later result:"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_seventy_two_transfer_cases_verify_independently(self):
        self.assertEqual(module.check(), 72)

    def test_existing_course_and_saved_progress_are_unmodified(self):
        text = (ROOT / "_reports/poker-transfer/README.md").read_text()
        self.assertIn("No existing site data, pages, scripts, CSS", text)
        self.assertIn("pending", text.lower())
        self.assertEqual(len(module.LESSONS), 6)
        self.assertIn("separate A/B protocol", text)
        self.assertTrue((ROOT / "_reports/poker-transfer/session-form.md").exists())
        self.assertEqual(len(list((ROOT / "_reports/poker-transfer/cards").glob("S?-?.md"))), 72)
        for slug in module.LESSONS:
            self.assertTrue((ROOT / "_source/poker" / (slug + ".html")).exists())

    @contextmanager
    def changed_case(self, case_id, change):
        """Re-render a corrupted source so the mechanical check, not drift, rejects it."""
        with tempfile.TemporaryDirectory() as folder:
            copied = Path(folder) / "packet"
            shutil.copytree(module.FOLDER, copied)
            target = copied / "cases.json"
            data = json.loads(target.read_text())
            change(next(case for case in data["cases"] if case["id"] == case_id))
            target.write_text(json.dumps(data))
            spec = spec_from_file_location("mutated_transfer_builder", copied / "build_packet.py")
            builder = module_from_spec(spec)
            spec.loader.exec_module(builder)
            for name, content in builder.outputs(data).items():
                (copied / name).write_text(content)
            with patch.object(module, "FOLDER", copied):
                yield

    def test_rejects_wrong_expanded_call_even_when_all_views_agree(self):
        def corrupt(case):
            case["call"]["answer"] += 1
        with self.changed_case("S1-C", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_expanded_action_order(self):
        def corrupt(case):
            order = case["action_order"]
            order["next"] = next(seat for seat in order["active"] if seat != order["hero"])
        with self.changed_case("S2-C", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_opponent_comparison_even_when_all_views_agree(self):
        def corrupt(case):
            old = case["expected_comparisons"][0]
            case["expected_comparisons"][0] = "stronger" if old != "stronger" else "weaker"
        with self.changed_case("S5-C", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_river_fraction(self):
        def corrupt(case):
            case["river"]["num"] += 1
        with self.changed_case("S4-C", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_wrong_full_reraise_total(self):
        def corrupt(case):
            case["full_raise"]["minimum_total"] += 3
        with self.changed_case("S1-I", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_unspecified_response_must_omit_action(self):
        def corrupt(case):
            case["responses"][0]["action"] = None
        with self.changed_case("S6-F", corrupt):
            with self.assertRaises(AssertionError):
                module.check()

    def test_straight_completion_check_requires_both_ends(self):
        case = {"id": "fixture", "hero": ["9h", "8d"], "board": ["7c", "6s", "Kh"],
                "draw": {"suit": None, "suit_count": 0, "completion_ranks": ["5", "T"]}}
        module.check_draw(case)
        case["draw"]["completion_ranks"] = ["5"]
        with self.assertRaises(AssertionError):
            module.check_draw(case)

    def test_rejects_changes_to_original_ab_source(self):
        with self.changed_case("S1-A", lambda case: case.update(prompt=case["prompt"] + " Answer hint.")):
            with self.assertRaises(AssertionError):
                module.check()

    def test_rejects_expanded_skill_copy_drift(self):
        with self.changed_packet("study/S6.md", "Compare your explanation", "Answer missing"):
            with self.assertRaises(AssertionError):
                module.check()

    def test_all_draft_holdings_match_existing_independent_js_evaluator(self):
        data = json.loads((module.FOLDER / "cases.json").read_text())
        holdings, expected = [], []
        for case in data["cases"]:
            if not case["board"]:
                continue
            cards = case["hero"] + case["board"]
            holdings.append(cards)
            expected.append(case["expected_rank"])
            for candidate in case.get("candidates", []):
                if set(candidate).isdisjoint(cards):
                    holdings.append(candidate + case["board"])
                    expected.append(list(module.best(candidate + case["board"])))
        code = "const h=require('./assets/poker-hand-lab.js'); const rows=JSON.parse(require('node:fs').readFileSync(0,'utf8')); process.stdout.write(JSON.stringify(rows.map(c=>c.length===5?h.scoreFive(c):h.bestFive(c).score)));"
        run = subprocess.run(["node", "-e", code], cwd=ROOT, input=json.dumps(holdings),
                             text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), expected)

    def test_zero_owed_blind_and_unopened_round_have_distinct_actions(self):
        for to, expected in ((3, ["check", "raise"]), (0, ["check", "bet"])):
            case = {"id": "fixture", "call": {"to": to, "paid": to, "answer": 0},
                    "action": {"owed": 0, "check_allowed": True, "legal_actions": expected}}
            module.check_action(case)
            case["action"]["legal_actions"] = ["check", "bet"] if to else ["check", "raise"]
            with self.assertRaises(AssertionError):
                module.check_action(case)

if __name__ == "__main__":
    unittest.main()
