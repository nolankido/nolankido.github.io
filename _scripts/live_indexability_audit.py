"""Read-only live sitemap, indexability, schema and internal-link audit.

Run manually: python3 _scripts/live_indexability_audit.py
GET requests only; no dependencies, credentials, paid APIs, or scheduled jobs.
This checks public eligibility, never actual Google or Bing index inclusion.
"""

import concurrent.futures
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from search_metadata_contract import crawler_field, directives

BASE = "https://nolankido.com"
BOOK_ROUTES = ("/books/", "/books/one-workflow-at-a-time/",
               "/books/how-to-play-no-limit-texas-holdem/", "/books/ai-works-human-decides/")
EVIDENCE_ROUTES = (
    "/about/accounting-research/", "/ai-in-real-life/",
    "/technology/checking-ai-website-changes/",
    "/technology/rightsreceipt-ai-licensing/",
    "/technology/local-ai-review-replies/",
    "/technology/ai-book-continuity-checker/",
    "/technology/ai-poker-video-evidence/",
    "/technology/dinner-on-time/",
)
SAMPLE = [
    "/", "/about/", "/bio/", *BOOK_ROUTES, *EVIDENCE_ROUTES,
    "/technology/", "/technology/check-ai-answers/",
    "/technology/local-ai-gaming-laptop/",
    "/technology/review-reply-evidence-audit/", "/poker/", "/poker/library/",
    "/poker/resources/", "/poker/start-here/", "/poker/holdem-basics/",
    "/poker/six-to-ten-bb-tournament-decisions/", "/poker/satellite-bubble-seat-equity/",
    "/poker/poker-math/", "/poker/nolan-kido/",
    "/poker/episodes/portland-meadows-ep1/",
    "/poker/episodes/portland-meadows-standoff/", "/poker/study/",
    "/projects/", "/living-well/", "/living-well/tasks/learn-and-reflect/",
    "/creative/",
]
EXCLUDED = ["/find/", "/poker/find/", "/living-well/find/", "/card/", "/404.html"]
LIMIT = 2 * 1024 * 1024


def sitemap_inventory(document):
    """Reject malformed or noncanonical sitemap entries; never fetch foreign URLs."""
    paths, issues = [], []
    try:
        tree = ET.fromstring(document)
    except ET.ParseError:
        return [], [["/sitemap.xml", "invalid XML"]]
    if tree.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        return [], [["/sitemap.xml", "expected sitemap urlset"]]
    for node in tree.findall("{*}url"):
        locs = node.findall("{*}loc")
        url = locs[0].text if len(locs) == 1 else None
        if (not isinstance(url, str) or not url.startswith(BASE)
                or not re.fullmatch(r"/(?:[a-z0-9-]+/)*", url[len(BASE):])):
            issues.append(["/sitemap.xml", "invalid or noncanonical loc"])
            continue
        path = url[len(BASE):]
        if path in paths:
            issues.append([path, "duplicate sitemap location"])
        paths.append(path)
    if not paths:
        issues.append(["/sitemap.xml", "no valid canonical locations"])
    return paths, issues


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals = []
        self.robots = []
        self.links = []
        self.structured_data = []
        self.in_jsonld = False
        self.script_parts = []
        self.h1 = 0
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag == "meta":
            for attribute in ("name", "property"):
                name = (a.get(attribute) or "").strip().lower()
                if crawler_field(name):
                    self.robots.append((name, a.get("content") or ""))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.script_parts = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_jsonld:
            self.structured_data.append("".join(self.script_parts))
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_jsonld:
            self.script_parts.append(data)
        if self.in_title:
            self.title.append(data)


def fetch(path):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SiteReadOnlyAudit/1.0)"})
    try:
        try:
            response = urllib.request.urlopen(req, timeout=24)
        except urllib.error.HTTPError as exc:
            response = exc  # A real HTTP status is not a DNS/network failure.
        with response as resp:
            raw = resp.read(LIMIT + 1)
            result = {
                "path": path, "status": resp.status, "final_url": resp.url,
                "x_robots": resp.headers.get_all("X-Robots-Tag", []),
                "mime": resp.headers.get("Content-Type", ""),
            }
        if len(raw) > LIMIT:
            result["html_parser_error"] = "response exceeds audit limit"
            return result
    except (OSError, ValueError) as exc:
        return {"path": path, "error": repr(exc)}
    parser = PageParser()
    try:
        parser.feed(raw.decode("utf-8"))
        parser.close()
    except (UnicodeError, ValueError) as exc:
        result["html_parser_error"] = repr(exc)
    result.update({
        "canonical": parser.canonicals,
        "robots": parser.robots,
        "h1": parser.h1,
        "title": "".join(parser.title).strip(),
    })
    links = set()
    for link in parser.links:
        try:
            absolute = urllib.parse.urljoin(url, link)
            parts = urllib.parse.urlsplit(absolute)
            if parts.scheme == "https" and parts.netloc == "nolankido.com":
                links.add(urllib.parse.unquote(parts.path))
        except ValueError:
            result["html_parser_error"] = "invalid link URL"
    result["internal_links"] = sorted(links)
    types = Counter()
    person_ids = set()
    invalid_dates = []
    schema_errors = []
    for script in parser.structured_data:
        try:
            obj = json.loads(script)
        except ValueError as exc:
            schema_errors.append(str(exc))
            continue
        def walk(x):
            if isinstance(x, list):
                for v in x: walk(v)
            elif isinstance(x, dict):
                t = x.get("@type", [])
                types.update([t] if isinstance(t, str) else [v for v in t if isinstance(v, str)] if isinstance(t, list) else [])
                if t == "Person" or isinstance(t, list) and "Person" in t:
                    if isinstance(x.get("@id"), str): person_ids.add(x["@id"])
                for key in ("dateModified", "datePublished"):
                    if isinstance(x.get(key), str):
                        val = x[key]
                        try: dt.datetime.fromisoformat(val.replace("Z", "+00:00"))
                        except ValueError: invalid_dates.append([key, val])
                for v in x.values(): walk(v)
        walk(obj)
    result["schema_types"] = dict(types)
    result["person_ids"] = sorted(person_ids)
    result["bad_schema_dates"] = invalid_dates
    result["schema_errors"] = schema_errors
    return result


def blocks_indexing(row):
    values = [value for _, value in row.get("robots", [])] + row.get("x_robots", [])
    for value in values:
        # Use the generated-page directive parser on live responses too.
        # A bot-qualified exclusion counts; image-preview:none does not.
        for token in directives(value):
            if token in {"noindex", "none"}:
                return True
            name, sep, directive = token.partition(":")
            if sep and crawler_field(name) and directive in {"noindex", "none"}:
                return True
    return False


def assess(paths, rows, priority=SAMPLE, excluded=EXCLUDED):
    """Return explicit failures even when an expected route is wholly absent."""
    sitemap_set = set(paths)
    by_path = {r["path"]: r for r in rows}
    inbound = defaultdict(set)
    for r in rows:
        if (r.get("status") == 200 and r.get("final_url") == BASE + r["path"]
                and r["path"] in sitemap_set and not r.get("html_parser_error")):
            for p in r.get("internal_links", []):
                if p != r["path"]:
                    inbound[p].add(r["path"])
    issues = []
    for p in sorted(sitemap_set | set(priority)):
        r = by_path.get(p, {})
        if p not in sitemap_set: issues.append([p, "priority sample missing from sitemap"])
        if r.get("status") != 200: issues.append([p, "non-200 or fetch error"])
        if r.get("final_url") != BASE + p: issues.append([p, "redirect or final URL differs"])
        if r.get("canonical") != [BASE + p]: issues.append([p, "canonical mismatch"])
        if blocks_indexing(r): issues.append([p, "unexpected noindex"])
        if not r.get("mime", "").lower().startswith("text/html"): issues.append([p, "not HTML"])
        if r.get("html_parser_error"): issues.append([p, "HTML parsing or response size error"])
        if not inbound.get(p): issues.append([p, "no incoming links from other crawled pages"])
        if r.get("h1") != 1: issues.append([p, "missing or duplicate h1"])
        if not r.get("title"): issues.append([p, "missing title"])
        if r.get("bad_schema_dates"): issues.append([p, "invalid JSON-LD date"])
        if r.get("schema_errors") or not r.get("schema_types"): issues.append([p, "missing or invalid JSON-LD"])
    for p in excluded:
        r = by_path.get(p, {})
        if p in sitemap_set: issues.append([p, "excluded utility in sitemap"])
        if r.get("status") not in ({200, 404} if p == "/404.html" else {200}):
            issues.append([p, "excluded utility fetch/status failure"])
        if r.get("final_url") != BASE + p: issues.append([p, "excluded utility redirect or final URL differs"])
        if r.get("html_parser_error") or not r.get("mime", "").lower().startswith("text/html"):
            issues.append([p, "excluded utility HTML response failure"])
        if not blocks_indexing(r): issues.append([p, "excluded utility missing noindex"])
    return issues, inbound


def main():
    try:
        with urllib.request.urlopen(BASE + "/sitemap.xml", timeout=25) as response:
            if response.status != 200 or response.url != BASE + "/sitemap.xml":
                raise ValueError("sitemap response is not the exact canonical URL")
            sitemap = response.read(LIMIT + 1)
        if len(sitemap) > LIMIT:
            raise ValueError("sitemap exceeds audit limit")
        paths, issues = sitemap_inventory(sitemap)
        with urllib.request.urlopen(BASE + "/robots.txt", timeout=20) as response:
            if response.status != 200 or response.url != BASE + "/robots.txt":
                raise ValueError("robots response is not the exact canonical URL")
            robots_txt = response.read(LIMIT + 1).decode("utf-8")
        if len(robots_txt.encode("utf-8")) > LIMIT:
            raise ValueError("robots.txt exceeds audit limit")
    except (OSError, ValueError) as exc:
        print("ALL_ISSUES", json.dumps([["/sitemap.xml or /robots.txt", "fetch or parse failure: " + str(exc)]]), flush=True)
        print("RESULT FAIL", flush=True)
        return 1
    sitemap_set = set(paths)
    print("SITEMAP", len(paths), "UNIQUE", len(sitemap_set), flush=True)
    print("ROBOTS", repr(robots_txt[:1500]), flush=True)
    all_paths = sorted(sitemap_set | set(SAMPLE) | set(EXCLUDED))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        rows = list(pool.map(fetch, all_paths))
    by_path = {r["path"]: r for r in rows}
    page_issues, inbound = assess(paths, rows)
    issues.extend(page_issues)
    errors = [r for r in rows if "error" in r or r.get("status") != 200]
    print("CRAWL", len(rows), "NON_200_OR_FETCH_ERROR", len(errors), flush=True)
    for r in errors[:20]:
        print("FETCH_ERROR", json.dumps(r, sort_keys=True), flush=True)
    print("PATH | SITEMAP | STATUS | CANONICAL | ROBOTS | XROBOTS | INBOUND | H1 | SCHEMA | BAD_DATES | SCHEMA_ERRORS", flush=True)
    for p in SAMPLE + EXCLUDED:
        r = by_path.get(p, {"path": p, "error": "absent"})
        print(" | ".join([
            p, "yes" if p in sitemap_set else "no", str(r.get("status", r.get("error"))),
            ";".join(r.get("canonical", [])), ";".join(str(x) for x in r.get("robots", [])),
            ";".join(r.get("x_robots", [])), str(len(inbound.get(p, set()))),
            str(r.get("h1", "?")), ",".join(sorted(r.get("schema_types", {}))),
            str(r.get("bad_schema_dates", [])), str(r.get("schema_errors", [])),
        ]), flush=True)
    print("PERSON_IDS", json.dumps({p: by_path.get(p, {}).get("person_ids", []) for p in SAMPLE if by_path.get(p, {}).get("person_ids")}), flush=True)
    print("ALL_ISSUES", json.dumps(issues), flush=True)
    print("ALL_SITEMAP_ZERO_INBOUND", json.dumps([p for p in paths if not inbound.get(p)]), flush=True)
    print("ALL_SITEMAP_INVALID_SCHEMA", json.dumps([(r["path"], r.get("schema_errors", []), r.get("bad_schema_dates", [])) for r in rows if r.get("path") in sitemap_set and (r.get("schema_errors") or r.get("bad_schema_dates"))]), flush=True)
    print("RESULT", "PASS" if not issues else "FAIL", flush=True)
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())
