/* Local browser regressions for retaining an AI task-choice check. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const {expect} = require('playwright/test');

const ROOT = path.resolve(__dirname, '..');
const BASE = 'http://website.test';
const PAGE = '/technology/should-i-use-ai/';
const SOURCE = 'https://nolankido.com' + PAGE;
const GOOD = {goal: 'clear', inputs: 'allowed', stakes: 'low', review: 'ready', simpler: 'no', scope: 'draft'};
const CAUTIONS = {goal: 'unclear', inputs: 'restricted', stakes: 'high', review: 'missing', simpler: 'unknown', scope: 'action'};
const MIME = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.woff2': 'font/woff2', '.txt': 'text/plain', '.xml': 'application/xml', '.ico': 'image/x-icon'};
const summary = {pass: false, outcomes: 0, downloadedRecords: 0, clipboardCases: 0, delayedClipboardCases: 0,
  exportGuards: 0, downloadFailures: 0, invalidations: 0, normalLayouts: 0, enlargedTextLayouts: 0,
  printCases: 0, printPDFs: 0, keyboardJourneys: 0, noScriptCases: 0, privacyChecks: 0, screenshots: 0};
const pageErrors = [];
let browser;
let context;
let page;
let requests = [];

async function launch(javaScriptEnabled = true) {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROMIUM_PATH ? {executablePath: process.env.CHROMIUM_PATH} : {}),
    args: ['--no-sandbox', '--single-process', '--no-zygote', '--disable-gpu']
  });
  context = await browser.newContext({acceptDownloads: true, javaScriptEnabled, reducedMotion: 'reduce',
    viewport: {width: 390, height: 1000}});
  requests = [];
  context.on('request', request => requests.push(request.url()));
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin !== BASE) return route.abort();
    try {
      let relative = decodeURIComponent(url.pathname);
      if (relative.endsWith('/')) relative += 'index.html';
      const file = path.resolve(ROOT, '.' + relative);
      if (!file.startsWith(ROOT + path.sep)) return route.abort();
      await route.fulfill({status: 200, contentType: MIME[path.extname(file)] || 'application/octet-stream',
        body: await fs.promises.readFile(file), headers: {'cache-control': 'no-store'}});
    } catch (_) {
      await route.fulfill({status: 404, contentType: 'text/plain', body: 'Local fixture not found'});
    }
  });
  page = await context.newPage();
  page.setDefaultTimeout(7000);
  page.on('pageerror', error => pageErrors.push(String(error)));
}
async function load() {
  await page.goto(BASE + PAGE);
  await expect(page.locator('#choice-form')).toBeVisible();
  await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; });
}
async function choose(changes = {}) {
  const answers = {...GOOD, ...changes};
  for (const [key, value] of Object.entries(answers)) {
    await page.locator('#choice-' + key + '-' + value).check();
  }
  await page.locator('#choice-form button[type="submit"]').click();
  await expect(page.locator('#choice-result')).toBeVisible();
  return page.locator('#choice-record').textContent();
}
async function recordMatchesVisibleDecision() {
  const data = await page.evaluate(() => {
    const record = document.getElementById('choice-record').textContent;
    const selected = Array.from(document.querySelectorAll('#choice-form fieldset')).map(fieldset => {
      const radio = fieldset.querySelector('input:checked');
      return [fieldset.querySelector('legend').textContent.trim(),
        radio.closest('label').querySelector('span').textContent.trim()];
    });
    return {record, selected,
      title: document.getElementById('choice-result-title').textContent,
      next: document.getElementById('choice-next').textContent,
      reasons: Array.from(document.querySelectorAll('#choice-reasons li'), li => li.textContent),
      boundary: document.getElementById('choice-boundary').textContent,
      limits: document.getElementById('choice-limits').textContent,
      route: document.querySelector('#choice-route a').getAttribute('href')};
  });
  assert.equal(data.selected.length, 6);
  assert.match(data.record, /Nolan Kido/);
  assert.ok(data.record.includes(SOURCE));
  let previous = -1;
  for (const [question, answer] of data.selected) {
    const position = data.record.indexOf(question);
    assert.ok(position > previous, 'All six questions retain their visible order');
    assert.ok(data.record.indexOf(answer, position) > position, 'The selected label follows its question');
    previous = position;
  }
  for (const text of [data.title, data.next, ...data.reasons, data.boundary, data.limits]) {
    assert.ok(text && data.record.includes(text), 'Record retains visible decision text: ' + text);
  }
  assert.ok(data.record.includes(new URL(data.route, SOURCE).href));
  assert.ok(!data.record.includes(BASE), 'Exports use the production source and next link');
  await expect(page.locator('#choice-result-title')).toBeFocused();
  return data.record;
}
async function clipboard(mode) {
  await page.evaluate(mode => {
    window.__choiceCopyCalls = [];
    window.__choicePendingCopy = null;
    const value = mode === 'unavailable' ? undefined : {writeText(text) {
      window.__choiceCopyCalls.push(text);
      if (mode === 'reject') return Promise.reject(new Error('Deliberate clipboard denial'));
      if (mode === 'deferred') return new Promise((resolve, reject) => {
        window.__choicePendingCopy = {resolve, reject};
      });
      return Promise.resolve();
    }};
    Object.defineProperty(navigator, 'clipboard', {configurable: true, value});
  }, mode);
}
async function selectedRecord(expected) {
  await expect(page.locator('#choice-record-details')).toHaveAttribute('open', '');
  await expect(page.locator('#choice-record')).toBeVisible();
  await expect(page.locator('#choice-record')).toBeFocused();
  assert.equal(await page.evaluate(() => window.getSelection().toString()), expected);
  await expect(page.locator('#choice-copy-status')).toContainText(/copy/i);
}
async function noRecord() {
  await expect(page.locator('#choice-result')).toBeHidden();
  await expect(page.locator('#choice-record')).toHaveText('');
  await expect(page.locator('#choice-copy-status')).toHaveText('');
  assert.equal(await page.locator('#choice-record-details').evaluate(el => el.open), false);
}
async function widthFits(label) {
  const data = await page.evaluate(() => ({width: innerWidth, document: document.documentElement.scrollWidth,
    body: document.body.scrollWidth}));
  assert.ok(data.document <= data.width && data.body <= data.width, label + ': ' + JSON.stringify(data));
}
async function screenshot(name) {
  if (!process.env.SCREENSHOT_DIR) return;
  fs.mkdirSync(process.env.SCREENSHOT_DIR, {recursive: true});
  await page.locator('#choice-record-section').scrollIntoViewIfNeeded();
  await page.screenshot({path: path.join(process.env.SCREENSHOT_DIR, name), fullPage: false});
  summary.screenshots += 1;
}
async function main() {
  await launch();
  const scenarios = [
    [{}, 'trial'], [{inputs: 'unknown'}, 'pause'], [{stakes: 'high'}, 'pause'],
    [{goal: 'unclear'}, 'prepare'], [{review: 'missing'}, 'prepare'],
    [{simpler: 'yes'}, 'simpler'], [{simpler: 'unknown'}, 'simpler'],
    [{scope: 'action'}, 'prepare'], [CAUTIONS, 'pause']
  ];
  for (const [answers, kind] of scenarios) {
    await load();
    await choose(answers);
    await expect(page.locator('#choice-result')).toHaveAttribute('data-kind', kind);
    await recordMatchesVisibleDecision();
    if (answers === CAUTIONS) await expect(page.locator('#choice-reasons li')).toHaveCount(6);
    summary.outcomes += 1;
  }

  // The downloaded bytes preserve both successful-trial and multiple-caution records.
  for (const answers of [{}, CAUTIONS]) {
    await load();
    const text = await choose(answers);
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('#choice-download').click()
    ]);
    assert.equal(download.suggestedFilename(), 'ai-task-check.txt');
    assert.equal(await fs.promises.readFile(await download.path(), 'utf8'), text);
    await expect(page.locator('#choice-copy-status')).toContainText(/download requested/i);
    await download.delete();
    summary.downloadedRecords += 1;
  }

  for (const mode of ['success', 'reject', 'unavailable']) {
    await load();
    const text = await choose();
    await clipboard(mode);
    await page.locator('#choice-copy').focus();
    await page.keyboard.press('Enter');
    if (mode === 'success') {
      await expect(page.locator('#choice-copy-status')).toContainText(/copied/i);
      assert.deepEqual(await page.evaluate(() => window.__choiceCopyCalls), [text]);
    } else await selectedRecord(text);
    summary.clipboardCases += 1;
  }
  await load();
  const manuallySelected = await choose();
  await page.locator('#choice-select').focus();
  await page.keyboard.press('Enter');
  await selectedRecord(manuallySelected);
  summary.clipboardCases += 1;

  // Deferred clipboard outcomes must not revive a superseded result or message.
  for (const action of ['change', 'reset', 'resubmit', 'select']) {
    for (const settle of ['resolve', 'reject']) {
      await load();
      await choose();
      await clipboard('deferred');
      await page.locator('#choice-copy').click();
      await page.waitForFunction(() => Boolean(window.__choicePendingCopy));
      if (action === 'change') await page.locator('#choice-inputs-unknown').check();
      if (action === 'reset') await page.locator('#choice-form button[type="reset"]').click();
      if (action === 'resubmit') await page.locator('#choice-form button[type="submit"]').click();
      if (action === 'select') await page.locator('#choice-select').click();
      const before = await page.evaluate(() => ({
        status: document.getElementById('choice-copy-status').textContent,
        error: document.getElementById('choice-error').textContent,
        open: document.getElementById('choice-record-details').open,
        record: document.getElementById('choice-record').textContent,
        selection: window.getSelection().toString()
      }));
      await page.evaluate(settle => {
        const pending = window.__choicePendingCopy;
        if (settle === 'resolve') pending.resolve();
        else pending.reject(new Error('Deliberate delayed clipboard denial'));
      }, settle);
      await page.evaluate(() => Promise.resolve());
      const after = await page.evaluate(() => ({
        status: document.getElementById('choice-copy-status').textContent,
        error: document.getElementById('choice-error').textContent,
        open: document.getElementById('choice-record-details').open,
        record: document.getElementById('choice-record').textContent,
        selection: window.getSelection().toString()
      }));
      assert.deepEqual(after, before, action + '/' + settle + ' cannot change the newer state');
      summary.delayedClipboardCases += 1;
    }
  }

  // Hidden and empty results cannot trigger programmatic export events.
  for (const state of ['hidden', 'empty-visible']) {
    await load();
    await clipboard('success');
    await page.evaluate(state => {
      window.__choiceBlobAttempts = 0;
      URL.createObjectURL = () => { window.__choiceBlobAttempts += 1; throw new Error('Unexpected export'); };
      if (state === 'empty-visible') document.getElementById('choice-result').hidden = false;
      for (const id of ['choice-copy', 'choice-download', 'choice-select']) document.getElementById(id).click();
    }, state);
    assert.equal(await page.evaluate(() => window.__choiceBlobAttempts), 0);
    assert.deepEqual(await page.evaluate(() => window.__choiceCopyCalls), []);
    await expect(page.locator('#choice-record')).toHaveText('');
    await expect(page.locator('#choice-copy-status')).toHaveText('');
    summary.exportGuards += 1;
  }

  // Deliberate local failures exercise recovery and resource cleanup.
  for (const failure of ['blob', 'object-url', 'activation']) {
    await load();
    const text = await choose(CAUTIONS);
    await page.evaluate(failure => {
      const originalCreate = URL.createObjectURL;
      const originalRevoke = URL.revokeObjectURL;
      const originalClick = HTMLAnchorElement.prototype.click;
      window.__choiceURLs = {created: [], revoked: []};
      if (failure === 'blob') window.Blob = class { constructor() { throw new Error('Deliberate Blob failure'); } };
      URL.createObjectURL = function (blob) {
        if (failure === 'object-url') throw new Error('Deliberate object URL failure');
        const url = originalCreate.call(URL, blob);
        window.__choiceURLs.created.push(url);
        return url;
      };
      URL.revokeObjectURL = function (url) {
        window.__choiceURLs.revoked.push(url);
        return originalRevoke.call(URL, url);
      };
      HTMLAnchorElement.prototype.click = function () {
        if (failure === 'activation' && this.hasAttribute('download')) throw new Error('Deliberate activation failure');
        return originalClick.call(this);
      };
    }, failure);
    await page.locator('#choice-download').click();
    await selectedRecord(text);
    await expect(page.locator('a[download][href^="blob:"]')).toHaveCount(0);
    if (failure === 'activation') {
      await page.waitForFunction(() => window.__choiceURLs.created.length === 1 &&
        window.__choiceURLs.revoked.includes(window.__choiceURLs.created[0]));
    } else assert.deepEqual(await page.evaluate(() => window.__choiceURLs.created), []);
    summary.downloadFailures += 1;
  }

  const invalidators = {
    change: async () => page.locator('#choice-inputs-unknown').check(),
    missing: async () => {
      await page.locator('#choice-goal-clear').evaluate(el => { el.checked = false; });
      await page.locator('#choice-form button[type="submit"]').click();
    },
    malformed: async () => {
      await page.locator('#choice-goal-clear').evaluate(el => { el.value = 'not-a-valid-answer'; });
      await page.locator('#choice-form button[type="submit"]').click();
    },
    reset: async () => page.locator('#choice-form button[type="reset"]').click(),
    pagehide: async () => page.evaluate(() => window.dispatchEvent(new Event('pagehide'))),
    bfcache: async () => page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})))
  };
  for (const [name, invalidate] of Object.entries(invalidators)) {
    await load();
    await choose();
    await page.locator('#choice-select').click();
    await invalidate();
    await noRecord();
    if (['reset', 'pagehide', 'bfcache'].includes(name)) {
      await expect(page.locator('#choice-form input:checked')).toHaveCount(0);
    }
    summary.invalidations += 1;
  }

  await load();
  const initialRequests = requests.length;
  const initialURL = page.url();
  await choose(CAUTIONS);
  await clipboard('success');
  await page.locator('#choice-copy').click();
  await expect(page.locator('#choice-copy-status')).toContainText(/copied/i);
  assert.deepEqual(requests.slice(initialRequests).filter(url => /^https?:/.test(url)), []);
  assert.equal(page.url(), initialURL);
  assert.equal(await page.evaluate(() => localStorage.length + sessionStorage.length), 0);
  assert.deepEqual(await context.cookies(), []);
  summary.privacyChecks += 1;

  for (const width of [320, 390, 768, 1440]) {
    for (const [answers, label] of [[{}, 'trial'], [CAUTIONS, 'pause']]) {
      await page.setViewportSize({width, height: 1000});
      await load();
      await choose(answers);
      await widthFits(label + '/' + width + '/closed');
      summary.normalLayouts += 1;
      await page.locator('#choice-record-details summary').click();
      await widthFits(label + '/' + width + '/open');
      summary.normalLayouts += 1;
      if (label === 'trial' && [390, 1440].includes(width)) await screenshot('choice-record-' + width + '.png');
    }
  }
  await page.setViewportSize({width: 320, height: 1100});
  await load();
  await choose(CAUTIONS);
  await page.addStyleTag({content: 'html{font-size:200%!important}p,li,label,summary{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'});
  await page.locator('#choice-select').click();
  await widthFits('320/200-percent-text');
  await selectedRecord(await page.locator('#choice-record').textContent());
  summary.enlargedTextLayouts += 1;
  await screenshot('choice-record-320-large.png');

  const worksheet = await fs.promises.readFile(path.join(ROOT, 'downloads/should-i-use-ai.txt'), 'utf8');
  for (const width of [390, 1440]) {
    await page.setViewportSize({width, height: 1000});
    await load();
    const text = await choose(CAUTIONS);
    assert.equal(await page.locator('#choice-record-details').evaluate(el => el.open), false);
    assert.equal(await page.locator('.choice-sheet').evaluate(el => el.open), false);
    await page.emulateMedia({media: 'print'});
    await expect(page.locator('#choice-form')).toBeHidden();
    await expect(page.locator('#choice-record')).toBeVisible();
    await expect(page.locator('.choice-sheet pre')).toBeVisible();
    assert.equal(await page.locator('#choice-record').textContent(), text);
    assert.equal(await page.locator('.choice-sheet pre').textContent(), worksheet);
    assert.equal(await page.locator('#choice-record').evaluate(el => getComputedStyle(el).maxHeight), 'none');
    await expect(page.locator('#choice-copy')).toBeHidden();
    await widthFits('print/' + width);
    if (width === 390) {
      const pdf = await page.pdf({format: 'A4', printBackground: false});
      assert.equal(pdf.subarray(0, 4).toString(), '%PDF');
      assert.ok(pdf.length > 10000);
      summary.printPDFs += 1;
    }
    summary.printCases += 1;
    await page.emulateMedia({media: 'screen'});
    assert.equal(await page.locator('#choice-record-details').evaluate(el => el.open), false);
  }

  await load();
  await choose();
  await page.locator('#choice-route a').focus();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(BASE + '/technology/task-brief/');
  await expect(page.locator('#brief-editor')).toBeVisible();
  summary.keyboardJourneys += 1;

  // A fresh Chromium process avoids single-process context teardown reuse.
  await context.close();
  await browser.close();
  browser = null;
  await launch(false);
  await page.goto(BASE + PAGE);
  await expect(page.locator('#choice-form')).toBeHidden();
  await expect(page.locator('#choice-result')).toBeHidden();
  await expect(page.locator('#choice-fallback')).toBeVisible();
  await page.locator('.choice-sheet summary').click();
  assert.equal(await page.locator('.choice-sheet pre').textContent(), worksheet);
  await expect(page.locator('a[download][href="/downloads/should-i-use-ai.txt"]')).toBeVisible();
  await page.setViewportSize({width: 320, height: 1000});
  await widthFits('no-JavaScript/320');
  summary.noScriptCases += 1;

  assert.deepEqual(pageErrors, []);
  summary.pageErrors = pageErrors.length;
  summary.pass = true;
  console.log(JSON.stringify(summary, null, 2));
}
main().catch(error => {
  summary.error = String(error.stack || error);
  summary.pageErrors = pageErrors;
  console.error(JSON.stringify(summary, null, 2));
  process.exitCode = 1;
}).finally(async () => {
  if (browser) await browser.close().catch(() => {});
});

