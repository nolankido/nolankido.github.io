/* Pure integer arithmetic plus a local-only, progressively enhanced interface. */
(function (root) {
  "use strict";
  const keys = ["manual", "assisted", "review", "count", "setup", "upkeep"];
  function parse(value, key) {
    if (typeof value !== "string" || value.length > 16) throw new Error("Enter a number for " + key + ".");
    const raw = value.trim();
    const whole = key === "count";
    if (!(whole ? /^\d+$/ : /^\d+(?:\.\d{1,2})?$/).test(raw)) {
      throw new Error(whole ? "Enter a whole repetition count from 1 to 100,000." : "Enter minutes from 0 to 100,000, using at most two decimal places. Use 0 when none.");
    }
    const parts = raw.split(".");
    const result = whole ? Number(parts[0]) : Number(parts[0]) * 100 + Number((parts[1] || "").padEnd(2, "0"));
    if (!Number.isSafeInteger(result) || result > (whole ? 100000 : 10000000) || result < ((whole || key === "manual") ? 1 : 0)) {
      throw new Error(key === "manual" ? "Usual time must be greater than zero and at most 100,000 minutes." : "The number is outside the stated range.");
    }
    return result;
  }
  function calculate(input) {
    const v = {};
    keys.forEach(key => { v[key] = parse(input[key], key); });
    const perRun = v.manual - v.assisted - v.review;
    const overhead = v.setup + v.upkeep;
    const usual = v.manual * v.count;
    const changed = overhead + (v.assisted + v.review) * v.count;
    const net = usual - changed;
    return Object.freeze({ usual, changed, net, perRun, overhead, count: v.count,
      breakEven: perRun > 0 ? Math.max(1, Math.ceil(overhead / perRun)) : null,
      firstSaving: perRun > 0 ? Math.floor(overhead / perRun) + 1 : null,
      reduction: 100 * net / usual });
  }
  const api = Object.freeze({ parse, calculate });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.WorkflowTime = api;
  if (typeof document === "undefined") return;
  const editor = document.getElementById("time-editor");
  if (!editor) return;
  const byId = id => document.getElementById(id);
  const fields = Object.fromEntries(keys.map(k => [k, byId("time-" + k)]));
  const result = byId("time-result"), status = byId("time-status"), report = byId("time-report");
  const quality = byId("time-quality"), basis = byId("time-basis");
  const examplePicker = byId("time-example-picker"), exampleConfirm = byId("time-example-confirm");
  const exampleNote = byId("time-example-origin");
  let exampleOrigin = "", pendingExample = null, exampleTrigger = null;
  function dismissExample() {
    if (exampleConfirm) exampleConfirm.hidden = true;
    pendingExample = null; exampleTrigger = null;
  }
  const moneyFree = n => (n / 100).toLocaleString("en-US", {minimumFractionDigits: 0, maximumFractionDigits: 2}) + " min";
  function invalidate() {
    dismissExample();
    result.hidden = true; report.value = ""; byId("time-copy-status").textContent = "";
    byId("time-clear-confirm").hidden = true;
  }
  function clearErrors() {
    keys.forEach(k => { fields[k].removeAttribute("aria-invalid"); byId("time-" + k + "-error").textContent = ""; });
  }
  function reset() {
    invalidate(); clearErrors(); keys.forEach(k => { fields[k].value = ""; });
    quality.value = "unknown"; basis.value = "estimate"; status.textContent = "";
    exampleOrigin = "";
    if (exampleNote) { exampleNote.hidden = true; exampleNote.textContent = ""; }
  }
  if (examplePicker && exampleConfirm && exampleNote && byId("time-example-yes") && byId("time-example-no")) {
    function loadExample(example) {
      reset(); keys.forEach(k => { fields[k].value = example.values[k]; });
      exampleOrigin = "Fictional example starting point: " + example.label + ". The starting values are illustrative, not observed results.";
      status.textContent = example.label + " example loaded. Review or adjust the values, then calculate. Quality has not been checked.";
      fields.manual.focus({preventScroll: true});
      fields.manual.scrollIntoView({block: "center", behavior: "instant"});
    }
    let available = 0;
    for (const button of examplePicker.querySelectorAll("[data-time-example]")) {
      let values;
      try {
        values = JSON.parse(button.dataset.timeExample);
        if (!values || Object.keys(values).length !== keys.length || !button.dataset.timeLabel) throw new Error("Incomplete example");
        calculate(values);
      } catch (_) { button.hidden = true; continue; }
      const example = {values, label: button.dataset.timeLabel};
      button.addEventListener("click", () => {
        if (keys.some(k => fields[k].value) || quality.value !== "unknown" || basis.value !== "estimate") {
          byId("time-clear-confirm").hidden = true;
          pendingExample = example; exampleTrigger = button;
          byId("time-example-message").textContent = "Load the fictional " + example.label.toLowerCase() + " example? This replaces all six values and resets the basis to planning estimates and quality to not yet checked.";
          exampleConfirm.hidden = false;
          byId("time-example-no").focus({preventScroll: true});
          exampleConfirm.scrollIntoView({block: "center", behavior: "instant"});
        } else loadExample(example);
      });
      available += 1;
    }
    byId("time-example-yes").addEventListener("click", () => {
      const example = pendingExample; dismissExample(); if (example) loadExample(example);
    });
    byId("time-example-no").addEventListener("click", () => {
      const button = exampleTrigger; dismissExample(); if (button) button.focus();
    });
    examplePicker.hidden = available === 0;
  }
  keys.forEach(k => fields[k].addEventListener("input", () => {
    const hadResult = !result.hidden; invalidate();
    fields[k].removeAttribute("aria-invalid"); byId("time-" + k + "-error").textContent = "";
    status.textContent = hadResult ? "Inputs changed. Calculate again for an up-to-date comparison." : "";
  }));
  [quality, basis].forEach(el => el.addEventListener("change", () => {
    invalidate(); status.textContent = "Comparison changed. Calculate again.";
  }));
  byId("time-calculate").addEventListener("click", () => {
    invalidate(); clearErrors();
    const input = Object.fromEntries(keys.map(k => [k, fields[k].value]));
    let first = null;
    keys.forEach(k => { try { parse(input[k], k); } catch (e) {
      fields[k].setAttribute("aria-invalid", "true"); byId("time-" + k + "-error").textContent = e.message;
      first = first || fields[k];
    }});
    if (first) { status.textContent = "Check the highlighted fields. Enter 0 for a cost that does not apply."; first.focus(); return; }
    if (!["unknown", "pass", "fail"].includes(quality.value) || !["estimate", "observed"].includes(basis.value)) return;
    const v = calculate(input);
    const outcome = v.net > 0 ? moneyFree(v.net) + " saved in this window" :
      v.net < 0 ? moneyFree(-v.net) + " extra time in this window" : "No net time saved in this window";
    byId("time-result-title").textContent = outcome;
    const gate = quality.value === "fail" ? "Quality check not met: a faster result is not an acceptable replacement. The arithmetic is shown for diagnosis, not as a recommendation." :
      quality.value === "unknown" ? "Quality is unverified: time savings alone do not establish usefulness. Compare outputs against the same acceptance standard before deciding." :
      "You marked the quality check as met. This calculator has not verified it. Consider privacy, reliability, enjoyment, and the people affected separately.";
    byId("time-quality-note").textContent = gate;
    byId("time-usual-total").textContent = moneyFree(v.usual);
    byId("time-changed-total").textContent = moneyFree(v.changed);
    byId("time-per-run").textContent = moneyFree(v.perRun);
    byId("time-overhead").textContent = moneyFree(v.overhead);
    let threshold;
    if (v.perRun > 0) threshold = "With setup and upkeep held fixed at these values, no net time loss starts at repetition " + v.breakEven.toLocaleString("en-US") + "; strictly positive time savings start at repetition " + v.firstSaving.toLocaleString("en-US") + ". Recalculate if upkeep grows with usage.";
    else if (v.perRun === 0 && v.overhead === 0) threshold = "The methods take equal time at every repetition count in this model. Repeating the task does not create a time saving.";
    else threshold = "There is no time-saving break-even at these per-task costs. Repetition does not recover the overhead unless the method changes.";
    byId("time-threshold").textContent = threshold;
    const precision = v.reduction !== 0 && Math.abs(v.reduction) < 0.05 ? "less than 0.1% " + (v.reduction > 0 ? "less" : "more") + " time" :
      Math.abs(v.reduction).toFixed(1) + "% " + (v.reduction >= 0 ? "less" : "more") + " time";
    byId("time-percent").textContent = precision + " versus the usual method";
    const basisText = basis.value === "estimate" ? "Planning estimate, not a measured outcome." : "User-entered observations, not independently verified or a causal experiment.";
    byId("time-basis-note").textContent = basisText;
    if (exampleNote) { exampleNote.textContent = exampleOrigin; exampleNote.hidden = !exampleOrigin; }
    report.value = ["WORKFLOW TIME COMPARISON", "https://nolankido.com/technology/ai-time-savings/", basisText,
      ...(exampleOrigin ? [exampleOrigin] : []),
      "", ...keys.map(k => k + ": " + input[k].trim() + (k === "count" ? " repetitions" : " minutes")),
      "", outcome, "Usual total: " + moneyFree(v.usual), "Changed total: " + moneyFree(v.changed),
      "Per-task difference before overhead: " + moneyFree(v.perRun), "Fixed overhead: " + moneyFree(v.overhead),
      precision, threshold, "", gate,
      "Model: N*(usual - assisted - review) - setup - upkeep. Compare the same task and quality. Count active effort consistently and avoid double-counting waiting. This is not a financial ROI or quality score."].join("\n") + "\n";
    result.hidden = false; status.textContent = "Comparison ready. Read the quality condition and assumptions.";
    byId("time-result-title").focus();
  });
  byId("time-copy").addEventListener("click", async () => {
    if (result.hidden || !report.value) return;
    const text = report.value;
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error("Unavailable");
      await navigator.clipboard.writeText(text);
      if (!result.hidden && report.value === text) byId("time-copy-status").textContent = "Comparison copied. Review it before sharing.";
    } catch (_) {
      if (!result.hidden && report.value === text) { report.focus(); report.select(); byId("time-copy-status").textContent = "Automatic copy is unavailable. Copy the selected text manually."; }
    }
  });
  byId("time-download").addEventListener("click", () => {
    if (result.hidden || !report.value) return;
    const text = report.value;
    let url, a;
    try {
      url = URL.createObjectURL(new Blob([text], {type:"text/plain;charset=utf-8"}));
      a = document.createElement("a"); a.href = url; a.download = "workflow-time-comparison.txt";
      a.hidden = true; document.body.appendChild(a); a.click();
      if (!result.hidden && report.value === text) byId("time-copy-status").textContent = "Text download requested. Keep the comparison in your own notes.";
    } catch (_) {
      if (!result.hidden && report.value === text) {
        report.focus(); report.select();
        byId("time-copy-status").textContent = "Download unavailable. Copy the selected comparison into your own notes.";
      }
    } finally {
      if (a) a.remove();
      if (url) setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  });
  byId("time-clear").addEventListener("click", () => {
    dismissExample();
    if (keys.some(k => fields[k].value)) { byId("time-clear-confirm").hidden = false; byId("time-clear-no").focus(); }
    else { reset(); fields.manual.focus(); }
  });
  byId("time-clear-yes").addEventListener("click", () => { reset(); status.textContent = "Entries cleared."; fields.manual.focus(); });
  byId("time-clear-no").addEventListener("click", () => { byId("time-clear-confirm").hidden = true; byId("time-clear").focus(); });
  root.addEventListener("pagehide", reset);
  root.addEventListener("pageshow", event => { if (event.persisted) reset(); });
  editor.hidden = false; byId("time-unavailable").hidden = true;
})(typeof window === "undefined" ? globalThis : window);
