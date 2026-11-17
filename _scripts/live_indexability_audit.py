"""Read-only live sitemap, indexability, schema and internal-link audit.

Run manually: python3 _scripts/live_indexability_audit.py
GET requests only; no dependencies, credentials, paid APIs, or scheduled jobs.
This checks public eligibility, never actual Google or Bing index inclusion.
"""

import concurrent.futures
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser

BASE = "https://nolankido.com"
SAMPLE = [
    "/", "/about/", "/technology/", "/technology/check-ai-answers/",
    "/technology/local-ai-review-replies/", "/technology/local-ai-gaming-laptop/",
    "/technology/review-reply-evidence-audit/", "/technology/ai-book-continuity-checker/",
    "/technology/rightsreceipt-ai-licensing/", "/poker/", "/poker/library/",
    "/poker/resources/", "/poker/start-here/", "/poker/holdem-basics/",
    "/poker/six-to-ten-bb-tournament-decisions/", "/poker/satellite-bubble-seat-equity/",
    "/poker/poker-math/", "/poker/nolan-kido/",
    "/poker/episodes/portland-meadows-ep1/",
    "/poker/episodes/portland-meadows-standoff/", "/poker/study/",
    "/projects/", "/living-well/", "/living-well/tasks/learn-and-reflect/",
    "/creative/",
]
EXCLUDED = ["/find/", "/poker/find/", "/living-well/find/", "/card/", "/404.html"]


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
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot", "bingbot"):
            self.robots.append((a.get("name", "").lower(), a.get("content", "")))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.in_title = True
        if tag == "script" and "application/ld+json" in a.get("type", "").lower():
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
        with urllib.request.urlopen(req, timeout=24) as resp:
            raw = resp.read(1100000)
            result = {
                "path": path, "status": resp.status, "final_url": resp.url,
                "x_robots": resp.headers.get_all("X-Robots-Tag", []),
                "mime": resp.headers.get("Content-Type", ""),
            }
    except Exception as exc:
        return {"path": path, "error": repr(exc)}
    parser = PageParser()
    try:
        parser.feed(raw.decode("utf-8", "replace"))
    except Exception as exc:
        result["html_parser_error"] = repr(exc)
    result.update({
        "canonical": parser.canonicals,
        "robots": parser.robots,
        "h1": parser.h1,
        "title": "".join(parser.title).strip(),
    })
    links = set()
    for link in parser.links:
        absolute = urllib.parse.urljoin(url, link)
        parts = urllib.parse.urlsplit(absolute)
        if parts.hostname == "nolankido.com":
            links.add(urllib.parse.unquote(parts.path))
    result["internal_links"] = sorted(links)
    types = Counter()
    person_ids = set()
    invalid_dates = []
    schema_errors = []
    for script in parser.structured_data:
        try:
            obj = json.loads(script)
        except Exception as exc:
            schema_errors.append(str(exc))
            continue
        def walk(x):
            if isinstance(x, list):
                for v in x: walk(v)
            elif isinstance(x, dict):
                t = x.get("@type", [])
                types.update([t] if isinstance(t, str) else [v for v in t if isinstance(v, str)])
                if t == "Person" or isinstance(t, list) and "Person" in t:
                    if x.get("@id"): person_ids.add(x["@id"])
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


def main():
    with urllib.request.urlopen(BASE + "/sitemap.xml", timeout=25) as response:
        sitemap = response.read().decode("utf-8", "replace")
    tree = ET.fromstring(sitemap)
    sitemap_paths = []
    for node in tree.findall(".//{*}loc"):
        u = urllib.parse.urlsplit(node.text or "")
        if u.hostname == "nolankido.com":
            sitemap_paths.append(u.path)
    sitemap_set = set(sitemap_paths)
    with urllib.request.urlopen(BASE + "/robots.txt", timeout=20) as response:
        robots_txt = response.read().decode("utf-8", "replace")

    print("SITEMAP", len(sitemap_paths), "UNIQUE", len(sitemap_set), flush=True)
    print("ROBOTS", repr(robots_txt[:1500]), flush=True)
    all_paths = sorted(set(sitemap_paths) | set(EXCLUDED))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        rows = list(pool.map(fetch, all_paths))
    by_path = {r["path"]: r for r in rows}
    inbound = defaultdict(set)
    for r in rows:
        for p in r.get("internal_links", []):
            inbound[p].add(r["path"])

    errors = [r for r in rows if "error" in r or r.get("status") != 200]
    print("CRAWL", len(rows), "ERRORS", len(errors), flush=True)
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
    print("PERSON_IDS", json.dumps({p: by_path[p].get("person_ids", []) for p in SAMPLE if by_path[p].get("person_ids")}), flush=True)

    issues = []
    for p in sitemap_paths:
        r = by_path.get(p, {})
        if r.get("status") != 200: issues.append([p, "non-200 or fetch error"])
        if r.get("final_url") != BASE + p: issues.append([p, "redirect or final URL differs"])
        if r.get("canonical") != [BASE + p]: issues.append([p, "canonical mismatch"])
        if any("noindex" in v.lower() for _, v in r.get("robots", [])) or any("noindex" in v.lower() for v in r.get("x_robots", [])):
            issues.append([p, "unexpected noindex"])
        if not inbound.get(p): issues.append([p, "no inbound links from all sitemap URLs"])
        if r.get("h1") != 1: issues.append([p, "missing or duplicate h1"])
        if r.get("bad_schema_dates"): issues.append([p, "invalid JSON-LD date"])
        if r.get("schema_errors"): issues.append([p, "invalid JSON-LD"])
    for p in SAMPLE:
        if p not in sitemap_set: issues.append([p, "priority sample missing from sitemap"])
    for p in EXCLUDED:
        r = by_path.get(p, {})
        noindex = any("noindex" in v.lower() for _, v in r.get("robots", [])) or any("noindex" in v.lower() for v in r.get("x_robots", []))
        if p in sitemap_set: issues.append([p, "excluded utility in sitemap"])
        if not noindex: issues.append([p, "excluded utility missing noindex"])
    print("ALL_ISSUES", json.dumps(issues), flush=True)
    print("ALL_SITEMAP_ZERO_INBOUND", json.dumps([p for p in sitemap_paths if not inbound.get(p)]), flush=True)
    print("ALL_SITEMAP_INVALID_SCHEMA", json.dumps([(r["path"], r["schema_errors"], r["bad_schema_dates"]) for r in rows if r.get("path") in sitemap_set and (r.get("schema_errors") or r.get("bad_schema_dates"))]), flush=True)
    print("RESULT", "PASS" if not issues else "FAIL", flush=True)
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())
