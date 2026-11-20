"""Regression checks for two canonical, source-backed Nolan Kido book pages."""
from pathlib import Path
import json
import re
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_scripts"))
sys.path.insert(0, str(ROOT / "_tests"))
import book_pages


class BookPublicationTests(unittest.TestCase):
    def test_both_book_pages_have_matching_sources_and_registered_routes(self):
        items = book_pages.published(ROOT)
        self.assertEqual({x["slug"] for x in items}, {x["slug"] for x in book_pages.BOOKS})

    def test_book_pages_are_indexable_and_identified_to_author(self):
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                page = (ROOT / "books" / book["slug"] / "index.html").read_text(encoding="utf-8")
                canonical = book_pages.ORIGIN + book_pages.route(book)
                self.assertEqual(page.count('<link rel="canonical" href="' + canonical + '">'), 1)
                self.assertEqual(page.count('<meta property="og:url" content="' + canonical + '">'), 1)
                self.assertNotIn('content="noindex', page)
                self.assertEqual(len(re.findall(r"<h1\b", page)), 1)
                match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                self.assertIsNotNone(match)
                record = json.loads(match.group(1))
                self.assertEqual(record["mainEntity"]["@id"], canonical + "#book")
                self.assertEqual(record["mainEntity"]["author"]["@id"], book_pages.PERSON)
                for forbidden in ("isbn", "offers", "bookFormat", "datePublished", "aggregateRating"):
                    self.assertNotIn(forbidden, record["mainEntity"])

    def test_companion_files_links_arithmetic_and_image_alt(self):
        companions = {
            "one-workflow-at-a-time": ("downloads/one-workflow-ai-pilot-worksheet.md",
                                       "4 + 3 + 7 + 1 = 15 minutes"),
            "how-to-play-no-limit-texas-holdem": ("downloads/holdem-river-call-check-worksheet.md",
                                                   "10 / 40 = 25%"),
        }
        creative = (ROOT / "_source/creative/home.html").read_text(encoding="utf-8")
        for item in book_pages.BOOKS:
            with self.subTest(slug=item["slug"]):
                path, example = companions[item["slug"]]
                worksheet = (ROOT / path).read_text(encoding="utf-8")
                page = (ROOT / "books" / item["slug"] / "index.html").read_text(encoding="utf-8")
                self.assertGreater(len(worksheet), 1500)
                self.assertIn("Free companion resource", worksheet)
                self.assertIn('href="/' + path + '"', page)
                self.assertIn('href="/' + path + '"', creative)
                self.assertIn(example, worksheet.replace("**", ""))
                self.assertIn("not an official cover of this book", page)
                self.assertNotIn(chr(0x2014), worksheet)

    def test_book_topic_social_cards_and_entity_links(self):
        cards = {
            "one-workflow-at-a-time": "ai-time-savings.png",
            "how-to-play-no-limit-texas-holdem": "reader-poker-no-limit-holdem-guide.png",
        }
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                route = book_pages.route(book)
                canonical = book_pages.ORIGIN + route
                page = (ROOT / route.lstrip("/") / "index.html").read_text(encoding="utf-8")
                asset = "assets/social/" + cards[book["slug"]]
                self.assertTrue((ROOT / asset).is_file())
                self.assertIn('<meta property="og:image" content="' + book_pages.ORIGIN + "/" + asset + '">', page)
                self.assertIn('<meta name="twitter:image" content="' + book_pages.ORIGIN + "/" + asset + '">', page)
                self.assertIn("not an official cover of this book", page)
                raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                self.assertIsNotNone(raw)
                schema = json.loads(raw.group(1))
                self.assertEqual(schema["about"]["@id"], canonical + "#book")
                self.assertEqual(schema["mainEntity"]["mainEntityOfPage"]["@id"], canonical + "#webpage")
                self.assertEqual(schema["mainEntity"]["author"]["@id"], book_pages.PERSON)

    def test_topic_guides_link_back_to_books_without_backdating(self):
        context = {
            "technology/ai-workflow-pilot/index.html": "/books/one-workflow-at-a-time/",
            "poker/poker-books-and-courses/index.html": "/books/how-to-play-no-limit-texas-holdem/",
            "poker/no-limit-holdem-guide/index.html": "/books/how-to-play-no-limit-texas-holdem/",
        }
        for path, route in context.items():
            with self.subTest(path=path):
                doc = (ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(doc.count('href="' + route + '"'), 1)
                self.assertIn('<meta property="article:modified_time" content="2026-11-20">', doc)
                raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S)
                self.assertIsNotNone(raw)
                schema = json.loads(raw.group(1))
                self.assertEqual(schema["dateModified"], "2026-11-20")

    def test_author_bibliography_links_to_exact_books_and_shared_identity(self):
        from html import unescape
        source = (ROOT / "_source/bio.html").read_text(encoding="utf-8")
        public = (ROOT / "bio/index.html").read_text(encoding="utf-8")
        finder = (ROOT / "find/index.html").read_text(encoding="utf-8")
        rich_source = json.loads((ROOT / "_source/person-schema.jsonld").read_text(encoding="utf-8"))
        rich_public = json.loads((ROOT / "assets/nolan-kido-identity.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(rich_source, rich_public)
        self.assertIn('id="profile-books"', source)
        self.assertIn('href="#profile-books"', source)
        self.assertIn("not independent confirmation of Amazon listing status", public)
        self.assertIn("two nonfiction books", unescape(finder))
        books = [node for node in rich_public["@graph"] if node["@type"] == "Book"]
        self.assertEqual(len(books), 2)
        ids = [node["@id"] for node in rich_public["@graph"]]
        self.assertEqual(len(ids), len(set(ids)))
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                url = book_pages.ORIGIN + book_pages.route(book)
                self.assertIn('href="' + book_pages.route(book) + '"', public)
                node = next(node for node in books if node["url"] == url)
                self.assertEqual(node["@id"], url + "#book")
                self.assertEqual(node["author"]["@id"], book_pages.PERSON)
                page = (ROOT / book_pages.route(book).lstrip("/") / "index.html").read_text(encoding="utf-8")
                actual = json.loads(re.search(
                    r'<script type="application/ld\+json">(.*?)</script>', page, re.S).group(1))["mainEntity"]
                self.assertEqual(node["name"], actual["name"])
                self.assertEqual(node["description"], actual["description"])
                self.assertEqual(node["mainEntityOfPage"], actual["mainEntityOfPage"])
                for unverified in ("offers", "isbn", "datePublished", "bookFormat", "aggregateRating"):
                    self.assertNotIn(unverified, node)
        meta = json.loads(re.search(
            r'<script type="application/ld\+json">(.*?)</script>', public, re.S).group(1))
        self.assertEqual(meta["dateModified"], "2026-11-20")
        self.assertIn("two nonfiction books", meta["description"])
        sitemap = ElementTree.parse(ROOT / "sitemap.xml")
        bio_rows = [item for item in sitemap.findall(".//{*}url")
                    if item.findtext("{*}loc") == "https://nolankido.com/bio/"]
        self.assertEqual(len(bio_rows), 1)
        self.assertEqual(bio_rows[0].findtext("{*}lastmod"), "2026-11-20")

    def test_website_audit_counts_the_two_standalone_book_canonicals(self):
        import build
        import check_search
        report = check_search.audit(ROOT, build.public_pages(), book_pages.ORIGIN)
        self.assertEqual(report.get('manual_book_pages'), len(book_pages.BOOKS))
        self.assertEqual(report['sitemap_urls'], len(set(
            item.text for item in ElementTree.parse(ROOT / 'sitemap.xml').iter()
            if item.tag.endswith('}loc'))))
        self.assertFalse(any('Sitemap must contain each indexable canonical exactly once'
                             in error for error in report['errors']))

    def test_live_byte_targets_cover_both_books_and_original_worksheets(self):
        import check_live
        targets = check_live.targets(ROOT)
        for item in book_pages.BOOKS:
            with self.subTest(slug=item['slug']):
                route = book_pages.route(item)
                public = ROOT / route.lstrip('/') / 'index.html'
                self.assertEqual(targets[route], (200, public.read_bytes()))
        for filename in ('one-workflow-ai-pilot-worksheet.md',
                         'holdem-river-call-check-worksheet.md'):
            path = ROOT / 'downloads' / filename
            self.assertEqual(targets['/downloads/' + filename], (200, path.read_bytes()))

    def test_html5_inventory_includes_both_book_pages(self):
        import check_html5
        import build
        paths = check_html5.publication_paths(ROOT, build.public_pages())
        for item in book_pages.BOOKS:
            with self.subTest(slug=item['slug']):
                route = book_pages.route(item)
                self.assertEqual(paths[route], Path(route.lstrip('/')) / 'index.html')
                self.assertEqual(check_html5.parse_errors((ROOT / paths[route]).read_text()), [])

    def test_book_release_is_mandatory_in_the_local_checklist(self):
        local = (ROOT / '_scripts/local_release_checks.py').read_text()
        self.assertIn("['_scripts/build_books.py', '--check']", local)
        self.assertIn("'test_book_pages.py'", local)

    def test_standalone_books_catalog_is_verified_and_discoverable(self):
        """The public Books landing page has its own canonical and only two works."""
        hub = book_pages.hub_record(ROOT)
        self.assertIsNotNone(hub)
        self.assertEqual(hub["url"], "https://nolankido.com/books/")
        public = (ROOT / book_pages.HUB_OUTPUT).read_text(encoding="utf-8")
        source = (ROOT / book_pages.HUB_SOURCE).read_text(encoding="utf-8")
        self.assertEqual(public, source)
        self.assertNotIn(chr(0x2014), public)
        self.assertEqual(len(re.findall(r"<h1\b", public)), 1)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                          public, re.S)
        self.assertIsNotNone(match)
        schema = json.loads(match.group(1))
        self.assertEqual(schema["@type"], "CollectionPage")
        self.assertEqual(schema["url"], hub["url"])
        self.assertEqual(schema["about"]["@id"], book_pages.PERSON)
        self.assertEqual(schema["mainEntity"]["@type"], "ItemList")
        items = schema["mainEntity"]["itemListElement"]
        self.assertEqual(len(items), 2)
        for order, book in enumerate(book_pages.BOOKS, start=1):
            item = items[order - 1]
            self.assertEqual(item["position"], order)
            self.assertEqual(item["item"]["@id"],
                             book_pages.ORIGIN + book_pages.route(book) + "#book")
            self.assertEqual(item["item"]["author"]["@id"], book_pages.PERSON)
            for field in ("datePublished", "offers", "isbn", "bookFormat",
                          "aggregateRating"):
                self.assertNotIn(field, item["item"])
        finder = (ROOT / "find/index.html").read_text(encoding="utf-8")
        self.assertEqual(finder.count('href="/books/"'), 1)
        packed = json.loads(re.search(
            r'<script type="application/json" id="find-section-data">(.*?)</script>',
            finder, re.S).group(1))
        self.assertIn("", packed["pages"]["books"])
        self.assertIn("books-catalog-verification", packed["pages"]["books"][""])
        xml = ElementTree.parse(ROOT / "sitemap.xml")
        locs = [node.text for node in xml.iter() if node.tag.endswith("}loc")]
        self.assertEqual(locs.count(hub["url"]), 1)
        for path in ("index.html", "creative/index.html", "about/index.html",
                     "bio/index.html"):
            self.assertIn('href="/books/"',
                          (ROOT / path).read_text(encoding="utf-8"))

    def test_books_catalog_is_a_required_release_target(self):
        import check_live
        import check_html5
        import build
        expected = (ROOT / book_pages.HUB_OUTPUT).read_bytes()
        self.assertEqual(check_live.targets(ROOT)["/books/"], (200, expected))
        self.assertEqual(check_html5.publication_paths(
            ROOT, build.public_pages())["/books/"], book_pages.HUB_OUTPUT)
        self.assertEqual(check_html5.parse_errors(expected.decode("utf-8")), [])
        import check_search
        report = check_search.audit(ROOT, build.public_pages(), book_pages.ORIGIN)
        self.assertEqual(report["manual_book_hubs"], 1)
        self.assertEqual(report["manual_book_pages"], 2)
        self.assertEqual(report["sitemap_urls"], 229)
        self.assertEqual(report["errors"], [])

    def test_books_catalog_fails_closed_on_partial_or_altered_sources(self):
        from tempfile import TemporaryDirectory
        import shutil
        with TemporaryDirectory() as temp:
            root = Path(temp)
            required = [
                book_pages.HUB_SOURCE, book_pages.HUB_OUTPUT,
                Path("index.html"), Path("creative/index.html"),
                Path("about/index.html"), Path("bio/index.html"),
            ]
            for book in book_pages.BOOKS:
                required.extend((Path("_source/books") / (book["slug"] + ".html"),
                                 Path("books") / book["slug"] / "index.html"))
            for path in required:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertIsNotNone(book_pages.hub_record(root))
            source = root / book_pages.HUB_SOURCE
            source.unlink()
            with self.assertRaisesRegex(ValueError, "requires source"):
                book_pages.hub_record(root)
            shutil.copyfile(ROOT / book_pages.HUB_SOURCE, source)
            target = root / book_pages.HUB_OUTPUT
            original = target.read_text(encoding="utf-8")
            altered = original.replace(
                '<link rel="canonical" href="https://nolankido.com/books/">',
                '<link rel="canonical" href="https://example.invalid/books/">', 1)
            self.assertNotEqual(original, altered)
            target.write_text(altered, encoding="utf-8")
            with self.assertRaises(ValueError):
                book_pages.hub_record(root)

    def test_sitemap_and_find_link_each_book_once(self):
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap = ElementTree.parse(ROOT / "sitemap.xml")
        site_urls = [element.text for element in sitemap.findall(".//s:loc", namespace)]
        finder = (ROOT / "find/index.html").read_text(encoding="utf-8")
        self.assertIn('<option value="book">Books</option>', finder)
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                path = book_pages.route(book)
                self.assertEqual(site_urls.count(book_pages.ORIGIN + path), 1)
                self.assertEqual(finder.count('href="' + path + '"'), 1)
                self.assertIn('data-kind="book"', finder)

    def test_internal_source_links_and_generated_book_schema_agree(self):
        home = (ROOT / "_source/home.html").read_text(encoding="utf-8")
        creative = (ROOT / "_source/creative/home.html").read_text(encoding="utf-8")
        public = (ROOT / "creative/index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', public, re.S)
        self.assertIsNotNone(m)
        items = json.loads(m.group(1))["mainEntity"]["itemListElement"]
        refs = {x["item"]["@id"] for x in items}
        for book in book_pages.BOOKS:
            with self.subTest(slug=book["slug"]):
                path = book_pages.route(book)
                self.assertIn('href="' + path + '"', home)
                self.assertIn('href="' + path + '"', creative)
                self.assertIn(book_pages.ORIGIN + path + "#book", refs)


if __name__ == "__main__":
    unittest.main()
