#!/usr/bin/env python3
"""Notify IndexNow of a verified public release; a dry run makes no requests.

Only canonical URLs in the two committed sitemaps can be selected. Cosmetic
stylesheet/chrome changes do not qualify by themselves. A successful receipt
means notification delivery, not crawling, indexing, ranking, or AI inclusion.

Protocol: https://www.indexnow.org/documentation
Change and retry guidance: https://www.indexnow.org/faq
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nolankido.com'
ENDPOINT = 'https://api.indexnow.org/indexnow'
MAIN_REF = 'https://api.github.com/repos/nolankido/nolankido.github.io/git/ref/heads/main'
KEY_FILE = 'fad988cb80ec4bc36cf2965cf1c64577.txt'
LIMIT = 2 * 1024 * 1024
MAX_URLS = 10000
MAX_ATTEMPTS = 3
MAX_RETRY_SECONDS = 30
SHA = re.compile(r'[0-9a-f]{40}\Z')
ROUTE = re.compile(r'/(?:[a-z0-9][a-z0-9-]*/)*\Z')
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


class NotificationError(ValueError):
    """A bounded validation or delivery failure, safe to put in a receipt."""


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise NotificationError('Redirect refused; use the exact canonical endpoint or URL.')


def request(method, url, body=None):
    """The only HTTP boundary. Tests inject a replacement and never send data."""
    headers = {'User-Agent': 'NolanKidoIndexNow/1.0', 'Accept-Encoding': 'identity'}
    if body is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        response = urllib.request.build_opener(NoRedirects()).open(req, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        data = response.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise NotificationError('HTTP response exceeded the size limit.')
        return response.code, dict(response.headers), data


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, check=False)
    if result.returncode:
        raise NotificationError('Required Git object or ancestor relationship is unavailable.')
    return result.stdout


def commit(root, value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise NotificationError('Base and head must be full lowercase 40-character commit IDs.')
    resolved = git(root, 'rev-parse', '--verify', value + '^{commit}').decode().strip()
    if resolved != value:
        raise NotificationError('Expected an exact commit object.')
    return value


def blob(root, revision, path, missing=False):
    result = subprocess.run(['git', 'cat-file', 'blob', revision + ':' + path], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    if result.returncode:
        if missing:
            return None
        raise NotificationError('A required committed public file is unavailable: ' + path)
    if len(result.stdout) > LIMIT:
        raise NotificationError('Committed public file exceeded the size limit: ' + path)
    return result.stdout


def route(url):
    try:
        parsed = urlsplit(url)
    except ValueError as error:
        raise NotificationError('Sitemap URL cannot be parsed.') from error
    if (parsed.scheme != 'https' or parsed.netloc != 'nolankido.com' or
            parsed.query or parsed.fragment or not ROUTE.fullmatch(parsed.path) or
            url != ORIGIN + parsed.path):
        raise NotificationError('Sitemap URL is outside the permitted canonical page routes.')
    return parsed.path


def sitemap(data):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise NotificationError('Sitemap declarations are not allowed.')
    try:
        document = ET.fromstring(data)
    except ET.ParseError as error:
        raise NotificationError('Sitemap is not valid XML.') from error
    if document.tag != '{' + NS['s'] + '}urlset':
        raise NotificationError('Expected the canonical sitemap urlset.')
    result = {}
    for item in document:
        locations = item.findall('s:loc', NS)
        dates = item.findall('s:lastmod', NS)
        if item.tag != '{' + NS['s'] + '}url' or len(locations) != 1 or len(dates) != 1:
            raise NotificationError('Each sitemap record needs one URL and one lastmod.')
        url, lastmod = locations[0].text or '', dates[0].text or ''
        route(url)
        if url in result or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', lastmod):
            raise NotificationError('Sitemap contains a duplicate URL or invalid date.')
        try:
            datetime.strptime(lastmod, '%Y-%m-%d')
        except ValueError as error:
            raise NotificationError('Sitemap lastmod is not a calendar date.') from error
        result[url] = lastmod
    if not result or len(result) > MAX_URLS:
        raise NotificationError('Sitemap URL count is outside the supported range.')
    return result


class Page(HTMLParser):
    """Compare page meaning, ignoring scripts, styles, and surrounding chrome."""
    def __init__(self, data, url, allow_noindex=False):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.main_count = 0
        self.in_title = False
        self.title_count = 0
        self.in_head = False
        self.skip = None
        self.json_text = None
        self.canonicals = []
        self.title = []
        self.words = []
        self.references = []
        self.metadata = []
        self.structured = []
        try:
            self.feed(data.decode('utf-8'))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise NotificationError('Canonical page contains invalid text or structured data.') from error
        if self.main_count != 1 or self.in_main or self.title_count != 1 or not self.title:
            raise NotificationError('Canonical page must contain one main and one nonempty title.')
        if self.canonicals != [url]:
            raise NotificationError('Page canonical does not match its sitemap URL.')
        self.noindex = any(name in ('robots', 'googlebot', 'bingbot') and
                           bool({'noindex', 'none'} & set(re.split(r'[\s,]+', value.lower())))
                           for name, value in self.metadata)
        if self.noindex and not allow_noindex:
            raise NotificationError('A current sitemap page is marked noindex.')
        value = [self.title, self.words, self.references, sorted(self.metadata), self.structured]
        self.digest = sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if self.in_head and tag == 'link' and 'canonical' in values.get('rel', '').split():
            self.canonicals.append(values.get('href'))
        if self.in_head and tag == 'meta':
            name = values.get('name', '').lower()
            if name in ('description', 'robots', 'googlebot', 'bingbot'):
                self.metadata.append((name, values.get('content', '')))
        if self.in_head and tag == 'title':
            self.in_title = True
            self.title_count += 1
        if self.in_head and tag == 'script' and values.get('type') == 'application/ld+json':
            self.json_text = []
        if tag == 'main':
            self.main_count += 1
            self.in_main = True
        if self.in_main:
            if tag in ('script', 'style'):
                self.skip = tag
            elif not self.skip:
                selected = {key: value for key, value in values.items()
                            if key in ('href', 'src', 'alt', 'aria-label', 'id', 'name', 'value', 'type')}
                if selected:
                    self.references.append((tag, sorted(selected.items())))

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_text is not None:
            self.structured.append(json.loads(''.join(self.json_text)))
            self.json_text = None
        if tag == self.skip:
            self.skip = None
        if tag == 'main':
            self.in_main = False
        if tag == 'title':
            self.in_title = False
        if tag == 'head':
            self.in_head = False

    def handle_data(self, data):
        if self.json_text is not None:
            self.json_text.append(data)
        if self.in_title:
            self.title.extend(data.split())
        if self.in_main and not self.skip:
            self.words.extend(data.split())


@dataclass(frozen=True)
class Change:
    url: str
    kind: str
    expected_status: int
    expected_body: bytes


def select_changes(root, base, head):
    """Use committed canonical pages, not source paths or a blanket sitemap ping."""
    commit(root, base)
    commit(root, head)
    git(root, 'merge-base', '--is-ancestor', base, head)
    before = sitemap(blob(root, base, 'sitemap.xml'))
    after = sitemap(blob(root, head, 'sitemap.xml'))
    changes = []
    for url in sorted(before.keys() | after.keys()):
        path = route(url).lstrip('/') + 'index.html'
        old = blob(root, base, path, missing=True) if url in before else None
        new = blob(root, head, path, missing=True)
        if url in before and old is None:
            raise NotificationError('Previous sitemap points to a missing committed page.')
        if url in after:
            if new is None:
                raise NotificationError('Current sitemap points to a missing committed page.')
            current = Page(new, url)
            if url not in before:
                changes.append(Change(url, 'added', 200, new))
            elif before[url] != after[url] or Page(old, url).digest != current.digest:
                changes.append(Change(url, 'updated', 200, new))
        elif new is None:
            changes.append(Change(url, 'deleted', 404, blob(root, head, '404.html')))
        elif Page(new, url, allow_noindex=True).noindex:
            changes.append(Change(url, 'updated', 200, new))
        else:
            raise NotificationError('Removed sitemap URL still has an indexable page; review it first.')
    if len(changes) > MAX_URLS:
        raise NotificationError('Submission exceeds the protocol URL limit.')
    return changes


def key_value(root, head):
    key = blob(root, head, KEY_FILE).decode('utf-8')
    if not re.fullmatch(r'[a-zA-Z0-9-]{8,128}', key) or KEY_FILE != key + '.txt':
        raise NotificationError('Public root key file does not match the protocol.')
    return key


def current_main(head, send):
    status, _, data = send('GET', MAIN_REF)
    try:
        current = json.loads(data)['object']['sha']
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeError) as error:
        raise NotificationError('Could not verify the current public main commit.') from error
    if status != 200 or current != head:
        raise NotificationError('This commit is not the current public main release.')


def verify_live(root, head, changes, key, send):
    if git(root, 'rev-parse', 'HEAD').decode().strip() != head:
        raise NotificationError('Checkout HEAD does not match the submission commit.')
    current_main(head, send)
    status, _, data = send('GET', ORIGIN + '/' + KEY_FILE)
    if status != 200 or data != key.encode('utf-8'):
        raise NotificationError('Public root proof file is not deployed with the expected bytes.')
    for change in changes:
        status, headers, data = send('GET', change.url)
        if status != change.expected_status or data != change.expected_body:
            raise NotificationError('A selected public URL does not match the committed release: ' + change.url)
        robot = next((v for k, v in headers.items() if k.lower() == 'x-robots-tag'), '')
        if (change.expected_status == 200 and
                {'noindex', 'none'} & set(re.split(r'[\s,:]+', robot.lower())) and
                not Page(change.expected_body, change.url, allow_noindex=True).noindex):
            raise NotificationError('An indexable public URL is blocked by X-Robots-Tag.')
    current_main(head, send)


def retry_delay(headers, attempt, now):
    value = next((v for k, v in headers.items() if k.lower() == 'retry-after'), None)
    if value is None:
        return min(5 * attempt, MAX_RETRY_SECONDS)
    if re.fullmatch(r'\d+', value):
        seconds = int(value)
    else:
        try:
            when = parsedate_to_datetime(value)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            seconds = max(0, (when - now()).total_seconds())
        except (ValueError, TypeError, OverflowError) as error:
            raise NotificationError('Invalid Retry-After; retry later after reviewing the receipt.') from error
    if seconds > MAX_RETRY_SECONDS:
        raise NotificationError('Retry-After exceeds the bounded wait; defer this notification.')
    return seconds


def deliver(payload, receipt, send, sleep, now, guard):
    data = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if attempt > 1:
            guard()
        receipt['attempts'] = attempt
        try:
            status, headers, _ = send('POST', ENDPOINT, data)
            receipt['http_status'] = status
        except (TimeoutError, OSError, urllib.error.URLError):
            status, headers = None, {}
            receipt['http_status'] = None
        if status in (200, 202):
            receipt['status'] = 'received' if status == 200 else 'key_validation_pending'
            receipt['message'] = ('URLs received; crawling and indexing remain unverified.' if status == 200
                                  else 'URLs received; key validation and indexing remain unverified.')
            return
        if status not in (None, 429) and not (isinstance(status, int) and 500 <= status <= 599):
            raise NotificationError('IndexNow rejected the request; check HTTP status before retrying.')
        if attempt == MAX_ATTEMPTS:
            raise NotificationError('Transient notification failure after the bounded attempts.')
        if status == 429 and not any(k.lower() == 'retry-after' for k in headers):
            raise NotificationError('Rate limited without Retry-After; defer at least ten minutes.')
        delay = retry_delay(headers, attempt, now)
        receipt['retry_waits_seconds'].append(delay)
        sleep(delay)


def run(root, base, head, submit=False, send=request, sleep=time.sleep,
        now=lambda: datetime.now(timezone.utc)):
    receipt = {'version': 1, 'mode': 'submit' if submit else 'dry-run',
               'base_commit': base, 'head_commit': head, 'endpoint': ENDPOINT,
               'status': 'failed', 'urls': [], 'count': 0, 'attempts': 0,
               'http_status': None, 'retry_waits_seconds': [],
               'indexing_verified': False, 'timestamp': now().isoformat()}
    try:
        changes = select_changes(root, base, head)
        receipt['urls'] = [{'url': item.url, 'change': item.kind} for item in changes]
        receipt['count'] = len(changes)
        key = key_value(root, head)
        if not changes:
            receipt.update(status='nothing_to_submit', message='No meaningful canonical page changes.')
        elif not submit:
            receipt.update(status='planned', message='Dry run only; no network requests were made.')
        else:
            verify_live(root, head, changes, key, send)
            receipt['live_verified_commit'] = head
            deliver({'host': 'nolankido.com', 'key': key,
                     'keyLocation': ORIGIN + '/' + KEY_FILE,
                     'urlList': [change.url for change in changes]}, receipt, send, sleep, now,
                    lambda: current_main(head, send))
    except (NotificationError, UnicodeError, TimeoutError, OSError, urllib.error.URLError) as error:
        message = str(error) if isinstance(error, NotificationError) else 'Network or local read failed; notification is unverified.'
        receipt.update(status='failed', message=message)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='Exact previous deployed commit ID.')
    parser.add_argument('--head', required=True, help='Exact current deployed commit ID.')
    parser.add_argument('--submit', action='store_true', help='Verify public bytes, then notify IndexNow.')
    args = parser.parse_args()
    receipt = run(ROOT, args.base, args.head, submit=args.submit)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if receipt['status'] == 'failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
