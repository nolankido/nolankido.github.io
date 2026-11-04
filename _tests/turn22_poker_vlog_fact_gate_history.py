"""Test-only exact predecessor for Turn 22's structured poker-vlog fact gate.

This rewinds only the reviewed full Git blobs. Unknown mutations pass through
unchanged. No production code or downloaded checker imports this helper.
"""
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOBS = {
    "_source/technology/home.html": (
        "c7ffe2486205a27f29bc0f494f7019cb8699af25",
        "31a8cc92fd8d2d7cb60b02cea76dbe6e3402c93e",
    ),
    "technology/index.html": (
        "0f164e93bceed0d54d962a73adf3a5a69aa27051",
        "b2c87d335e4c42e7867d3a7ee6e366c43074feac",
    ),
    "downloads/poker-vlog-truth-to-screen-qa.md": (
        "3d1db5736a2e1c1f33449a6690db6a4a8d75637d",
        "c91a803e06586af3fceb4a95588fe391602dc82f",
    ),
}
ADDED = {"downloads/poker-vlog-fact-gate.py": "af85b4a1c9e0ef587bd376b15ca07877e8cd8cbc"}
INSERTIONS = {
    "_source/technology/home.html": "<section class=\"section folio-row\" id=\"poker-vlog-qa-demo\" aria-labelledby=\"poker-vlog-qa-demo-title\">\n  <div class=\"section-meta\"><p class=\"section-label\">Worked example / Offline QA</p></div>\n  <div class=\"section-content prose\">\n    <h2 class=\"section-title\" id=\"poker-vlog-qa-demo-title\">Seven constructed edit conflicts. Seven targeted flags.</h2>\n    <p>To make the <a href=\"#poker-vlog-qa\">truth-to-screen release gate</a> testable, I wrote a small standard-library Python checker for structured edit claims from the <a href=\"/poker/episodes/portland-meadows-ep1/\">public Portland Meadows Episode 1 record</a>. This is a deterministic audit of text fields, not an AI watching my footage. I constructed four fictional, incorrect scene records and paired each with a corrected record. The checker found the seven expected targeted conflicts in the constructed records and none in the corrected examples.</p>\n    <div class=\"project-table-scroll\" role=\"region\" aria-label=\"Synthetic poker scene before and after findings\" tabindex=\"0\">\n      <table>\n        <caption>Reproducible demonstrations, not observed defects in a released video</caption>\n        <thead><tr><th scope=\"col\">Constructed before edit</th><th scope=\"col\">Targeted flags</th><th scope=\"col\">Corrected after edit</th></tr></thead>\n        <tbody>\n          <tr><th scope=\"row\">Unverified suits and complete board shown as factual</th><td>2: suits, board</td><td>Omit the unverified details: 0</td></tr>\n          <tr><th scope=\"row\">Pocket sevens shown at 18 BB with a 2 BB button open</th><td>2: stack, raise-to amount</td><td>19.5 BB and 2.5 BB from the reported chips: 0</td></tr>\n          <tr><th scope=\"row\">Advertised $5,100 shown as the amount received</th><td>1: payout conflict</td><td>Report $2,900 after the four-way deal: 0</td></tr>\n          <tr><th scope=\"row\">A verified solver verdict and old version 7 chapter offset are claimed</th><td>2: unsupported solver, unverified chapter timing</td><td>Remove both unsupported assertions: 0</td></tr>\n        </tbody>\n      </table>\n    </div>\n    <p><a href=\"/downloads/poker-vlog-fact-gate.py\" download>Download the standalone Python checker (.py)</a>. Its built-in <code>--self-test</code> reproduces the four comparisons and confirms the expected seven-to-zero flag counts. <code>--example</code> prints a local JSON starter record, and <code>--check SCENES.json</code> checks only supplied structured scene fields. The <a href=\"/downloads/poker-vlog-truth-to-screen-qa.md\" download>worksheet</a> contains the commands and the final human review checklist. No model, account, uploaded video, internet connection or paid API is required.</p>\n    <p class=\"small-copy\"><strong>What this does not establish:</strong> The four before cases are deliberately written test fixtures, not flaws observed in an actual edit or model-generated mistakes. A clean structured result does not confirm that spoken audio matches graphics, establish missing suits, verify solver strategy, secure filming rights or predict viewer retention. The checker's sources are bounded to those three public Episode 1 fact records; other hands require separate human verification.</p>\n  </div>\n</section>\n",
    "technology/index.html": "<section class=\"section folio-row\" id=\"poker-vlog-qa-demo\" aria-labelledby=\"poker-vlog-qa-demo-title\">\n  <div class=\"section-meta\"><p class=\"section-label\">Worked example / Offline QA</p></div>\n  <div class=\"section-content prose\">\n    <h2 class=\"section-title\" id=\"poker-vlog-qa-demo-title\">Seven constructed edit conflicts. Seven targeted flags.</h2>\n    <p>To make the <a href=\"#poker-vlog-qa\">truth-to-screen release gate</a> testable, I wrote a small standard-library Python checker for structured edit claims from the <a href=\"/poker/episodes/portland-meadows-ep1/\">public Portland Meadows Episode 1 record</a>. This is a deterministic audit of text fields, not an AI watching my footage. I constructed four fictional, incorrect scene records and paired each with a corrected record. The checker found the seven expected targeted conflicts in the constructed records and none in the corrected examples.</p>\n    <div class=\"project-table-scroll\" role=\"region\" aria-label=\"Synthetic poker scene before and after findings\" tabindex=\"0\">\n      <table>\n        <caption>Reproducible demonstrations, not observed defects in a released video</caption>\n        <thead><tr><th scope=\"col\">Constructed before edit</th><th scope=\"col\">Targeted flags</th><th scope=\"col\">Corrected after edit</th></tr></thead>\n        <tbody>\n          <tr><th scope=\"row\">Unverified suits and complete board shown as factual</th><td>2: suits, board</td><td>Omit the unverified details: 0</td></tr>\n          <tr><th scope=\"row\">Pocket sevens shown at 18 BB with a 2 BB button open</th><td>2: stack, raise-to amount</td><td>19.5 BB and 2.5 BB from the reported chips: 0</td></tr>\n          <tr><th scope=\"row\">Advertised $5,100 shown as the amount received</th><td>1: payout conflict</td><td>Report $2,900 after the four-way deal: 0</td></tr>\n          <tr><th scope=\"row\">A verified solver verdict and old version 7 chapter offset are claimed</th><td>2: unsupported solver, unverified chapter timing</td><td>Remove both unsupported assertions: 0</td></tr>\n        </tbody>\n      </table>\n    </div>\n    <p><a href=\"/downloads/poker-vlog-fact-gate.py\" download>Download the standalone Python checker (.py)</a>. Its built-in <code>--self-test</code> reproduces the four comparisons and confirms the expected seven-to-zero flag counts. <code>--example</code> prints a local JSON starter record, and <code>--check SCENES.json</code> checks only supplied structured scene fields. The <a href=\"/downloads/poker-vlog-truth-to-screen-qa.md\" download>worksheet</a> contains the commands and the final human review checklist. No model, account, uploaded video, internet connection or paid API is required.</p>\n    <p class=\"small-copy\"><strong>What this does not establish:</strong> The four before cases are deliberately written test fixtures, not flaws observed in an actual edit or model-generated mistakes. A clean structured result does not confirm that spoken audio matches graphics, establish missing suits, verify solver strategy, secure filming rights or predict viewer retention. The checker's sources are bounded to those three public Episode 1 fact records; other hands require separate human verification.</p>\n  </div>\n</section>\n",
    "downloads/poker-vlog-truth-to-screen-qa.md": "## Optional offline check for structured scene claims\n\nA companion [Python fact-gate script](https://nolankido.com/downloads/poker-vlog-fact-gate.py) offers a narrow, **deterministic** check for this *one public episode*. It does not parse an MP4, hear the voiceover, read artwork, verify permission to film, or judge poker strategy.\n\nThe script recognizes only three public source records: `hand_64o`, `hand_77`, and `event_payout`. Its four deliberately constructed before/after scenes demonstrate **seven targeted flags before revision and zero after**. These are scripted editorial examples, not real production defects, AI model outputs, a general accuracy rate, or evidence that an earlier video was repaired.\n\nRun it from the directory where the Python file is saved. Only Python's standard library is required:\n\n```powershell\npy -3 poker-vlog-fact-gate.py --self-test\npy -3 poker-vlog-fact-gate.py --example > scenes.json\npy -3 poker-vlog-fact-gate.py --check scenes.json\n```\n\nOn macOS or Linux replace `py -3` with `python3`. The script reads only the JSON you explicitly name. Exit code `0` means no targeted flags, `2` means findings, and `1` means an input or self-test error. For actual edits, manually compare the current audio, the screen and stronger private sources, then return to the human release gate above. **No targeted flags never means approved.**\n\n",
}


def key(path):
    value = Path(path)
    if value.is_absolute():
        try:
            value = value.relative_to(ROOT)
        except ValueError:
            return value.as_posix()
    return value.as_posix()


def blob(value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def before(path, data):
    name = key(path)
    pair = BLOBS.get(name)
    if pair is None or blob(data) != pair[1]:
        return data
    binary = isinstance(data, bytes)
    current = data.decode("utf-8") if binary else data
    insertion = INSERTIONS[name]
    if current.count(insertion) != 1:
        raise ValueError("Turn 22 approved insertion is absent: " + name)
    restored = current.replace(insertion, "", 1)
    predecessor = restored.encode("utf-8") if binary else restored
    if blob(predecessor) != pair[0]:
        raise ValueError("Turn 22 exact predecessor Git blob mismatch: " + name)
    return predecessor


def is_added_file(path, data):
    expected = ADDED.get(key(path))
    return expected is not None and blob(data) == expected
