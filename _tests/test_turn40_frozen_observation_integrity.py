"""Turn 40: strict mode roster and exact submitted-question evidence.

These trials are synthetic. No AI services or websites are queried by tests.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "downloads" / "ai-answer-sprint-25-audit.py"
PANEL = ROOT / "downloads" / "ai-answer-sprint-25-prompts.csv"
FROZEN = ROOT / "_reports/visibility-sprint/assistant-answer-panel-v1-2026-11-17.csv"
ROSTER_BLANK = ROOT / "downloads/ai-answer-sprint-25-roster-blank.csv"
PROMPTS_BLANK = ROOT / "downloads/ai-answer-sprint-25-submitted-prompts-blank.csv"
SPEC = importlib.util.spec_from_file_location("answer_audit_turn40", AUDIT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def trial(prompt_id="NB01", assistant="Perplexity", mode="Standard Search"):
    return {
        "date": "2026-11-20", "prompt_id": prompt_id,
        "assistant": assistant, "mode": mode, "status": "completed",
        "clickable_link_verified": "no", "linked_url": "",
        "text_only_mention": "no", "answer_correctness": "unverified",
        "task_completed": "yes",
    }


def csv_data(fields, rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


class Turn40MethodTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.prompts = audit.load_prompts(PANEL)
        self.roster = [("Perplexity", "Standard Search"), ("ChatGPT", "Search")]

    def put(self, filename, fields, rows):
        p = Path(self.tmp.name) / filename
        p.write_text(csv_data(fields, rows), encoding="utf-8")
        return p

    def roster_file(self, roster=None):
        selected = self.roster if roster is None else roster
        return self.put("modes.csv", audit.ROSTER_FIELDS,
                        [dict(zip(audit.ROSTER_FIELDS, row)) for row in selected])

    def evidence_file(self, observations, override=None):
        entries = []
        for row in observations:
            entries.append({
                "prompt_id": row["prompt_id"], "assistant": row["assistant"],
                "mode": row["mode"],
                "submitted_prompt": self.prompts[row["prompt_id"]]["exact_prompt"],
            })
        if override:
            entries[0].update(override)
        return self.put("prompts.csv", audit.PROMPT_EVIDENCE_FIELDS, entries)

    def test_frozen_panel_bytes_remain_original(self):
        self.assertEqual(PANEL.read_bytes(), FROZEN.read_bytes())
        self.assertEqual(len(self.prompts), 25)
        self.assertEqual(self.prompts["NB01"]["segment"], "nonbranded")

    def test_public_templates_are_blank_and_do_not_contain_observations(self):
        self.assertEqual(ROSTER_BLANK.read_text().strip(), ",".join(audit.ROSTER_FIELDS))
        self.assertEqual(PROMPTS_BLANK.read_text().strip(),
                         ",".join(audit.PROMPT_EVIDENCE_FIELDS))
        self.assertNotIn(chr(0x2014), AUDIT.read_text())

    def test_roster_duplicate_and_empty_file_are_rejected(self):
        for bad in ([], [("Perplexity", "Search"), ("perplexity", "search")]):
            with self.subTest(roster=bad):
                with self.assertRaises(audit.InvalidPanel):
                    audit.load_roster(self.roster_file(bad))

    def test_roster_unknown_field_or_blank_label_is_rejected(self):
        file = self.put("bad.csv", ("assistant", "mode", "private_token"),
                        [{"assistant": "Example", "mode": "Search", "private_token": "secret"}])
        with self.assertRaises(audit.InvalidPanel):
            audit.load_roster(file)
        with self.assertRaises(audit.InvalidPanel):
            audit.load_roster(self.roster_file([("", "Search")]))

    def test_exact_prompt_evidence_accepted(self):
        rows = [trial()]
        count = audit.verify_submitted_prompts(self.evidence_file(rows), rows, self.prompts)
        self.assertEqual(count, 1)
        summary = audit.summarize(rows, "2026-11", 2, self.prompts,
                                  audit.load_roster(self.roster_file()), count)
        self.assertTrue(summary["roster_predeclared"])
        self.assertTrue(summary["submitted_prompt_text_checked"])
        self.assertEqual(summary["coverage"]["planned_trials"], 50)
        self.assertEqual(summary["coverage"]["completed_trials"], 1)
        self.assertEqual(summary["per_mode_coverage"][0]["completed_trials"], 1)
        self.assertEqual(summary["per_mode_coverage"][1]["missing_rows"], 25)
        self.assertEqual(summary["segments"]["nonbranded"]["sample_percent"], 0.0)
        self.assertEqual(summary["segments"]["branded"]["sample_percent"], None)
        self.assertNotIn(self.prompts["NB01"]["exact_prompt"], json.dumps(summary))

    def test_near_match_prompt_is_excluded_even_if_answer_was_observed(self):
        rows = [trial()]
        evidence = self.evidence_file(rows, {
            "submitted_prompt": "How do I verify an AI-written answer before relying it?"
        })
        with self.assertRaisesRegex(audit.InvalidPanel, "differs from frozen"):
            audit.verify_submitted_prompts(evidence, rows, self.prompts)

    def test_missing_and_duplicate_prompt_evidence_rejected(self):
        rows = [trial()]
        missing = self.put("missing.csv", audit.PROMPT_EVIDENCE_FIELDS, [])
        with self.assertRaisesRegex(audit.InvalidPanel, "Every completed"):
            audit.verify_submitted_prompts(missing, rows, self.prompts)
        twice = [dict(prompt_id="NB01", assistant="Perplexity", mode="Standard Search",
                      submitted_prompt=self.prompts["NB01"]["exact_prompt"])] * 2
        duplicated = self.put("twice.csv", audit.PROMPT_EVIDENCE_FIELDS, twice)
        with self.assertRaisesRegex(audit.InvalidPanel, "repeated trial"):
            audit.verify_submitted_prompts(duplicated, rows, self.prompts)

    def test_evidence_for_uncompleted_trial_rejected(self):
        rows = [trial()]
        rows[0].update(status="not_checked", clickable_link_verified="",
                       text_only_mention="", answer_correctness="", task_completed="")
        file = self.evidence_file(rows)
        with self.assertRaisesRegex(audit.InvalidPanel, "not a completed"):
            audit.verify_submitted_prompts(file, rows, self.prompts)

    def test_unregistered_or_wrong_spelling_of_assistant_mode_is_rejected(self):
        for assistant, mode in (("Perplexity", "Pro"), ("perplexity", "Standard Search")):
            with self.subTest(assistant=assistant, mode=mode):
                with self.assertRaises(audit.InvalidPanel):
                    audit.summarize([trial(assistant=assistant, mode=mode)],
                                    "2026-11", 2, self.prompts, self.roster, 1)

    def test_empty_panel_has_no_measured_rate_despite_roster(self):
        count = audit.verify_submitted_prompts(
            self.put("empty.csv", audit.PROMPT_EVIDENCE_FIELDS, []), [], self.prompts)
        summary = audit.summarize([], "2026-11", 2, self.prompts, self.roster, count)
        self.assertEqual(summary["status"], "no_completed_trials")
        self.assertEqual(summary["coverage"]["missing_rows"], 50)
        self.assertIsNone(summary["segments"]["nonbranded"]["sample_percent"])
        self.assertTrue(summary["submitted_prompt_text_checked"])

    def test_legacy_audit_remains_compatible_without_strict_files(self):
        summary = audit.summarize([trial()], "2026-11", 1, self.prompts)
        self.assertFalse(summary["roster_predeclared"])
        self.assertFalse(summary["submitted_prompt_text_checked"])
        self.assertIsNone(summary["per_mode_coverage"])

    def test_cli_rejects_one_strict_file_and_hides_private_path(self):
        observations = self.put("observations.csv", audit.OBSERVATION_FIELDS, [])
        secret_file = self.roster_file()
        command = [sys.executable, str(AUDIT), "--month", "2026-11",
                   "--expected-modes", "2", "--prompts", str(PANEL),
                   "--csv", str(observations), "--roster", str(secret_file)]
        p = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("both --roster and --submitted-prompts", p.stderr)
        self.assertNotIn(str(secret_file), p.stderr)

    def test_cli_strict_empty_panel_preserves_nullable_result(self):
        observations = self.put("observations.csv", audit.OBSERVATION_FIELDS, [])
        roster = self.roster_file()
        evidence = self.put("evidence.csv", audit.PROMPT_EVIDENCE_FIELDS, [])
        result = subprocess.run([sys.executable, str(AUDIT), "--month", "2026-11",
                                 "--expected-modes", "2", "--prompts", str(PANEL),
                                 "--csv", str(observations), "--roster", str(roster),
                                 "--submitted-prompts", str(evidence)],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["status"], "no_completed_trials")
        self.assertEqual(out["coverage"]["missing_rows"], 50)
        self.assertIsNone(out["segments"]["nonbranded"]["sample_percent"])
        self.assertNotIn(str(self.tmp.name), result.stdout)

    def test_release_inventory_contains_blank_evidence_templates(self):
        sys.path.insert(0, str(ROOT / "_scripts"))
        import check_live
        targets = check_live.targets()
        for file in (ROSTER_BLANK, PROMPTS_BLANK):
            route = "/downloads/" + file.name
            self.assertEqual(targets[route], (200, file.read_bytes()))
        release = (ROOT / "_scripts/local_release_checks.py").read_text()
        self.assertIn("test_turn40_frozen_observation_integrity.py", release)


if __name__ == "__main__":
    unittest.main()
