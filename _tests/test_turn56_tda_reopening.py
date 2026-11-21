"""Turn 56: independent TDA 2026 Rule 49 arithmetic, attribution and caveats."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"_source/poker/poker-rules-and-fair-play.html"
PUBLISHED=ROOT/"poker/poker-rules-and-fair-play/index.html"
BET_SOURCE=ROOT/"_source/poker/betting-and-pots.html"
BET_PUBLISHED=ROOT/"poker/betting-and-pots/index.html"
RULE="https://www.pokertda.com/view-poker-tda-rules/"
DEST="/poker/poker-rules-and-fair-play/#reopening-per-player"

class Links(HTMLParser):
    def __init__(self,source):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.hrefs=[]
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):self.ids.append(a["id"])
        if tag=="a":self.hrefs.append(a.get("href"))

def example(html):
    return re.findall(r'<p id="reopening-per-player">(.*?)</p>',html,re.S)

def errors(html):
    found=example(html)
    if len(found)!=1:return ["missing or repeated Rule 49 answer"]
    body=found[0];result=[]
    for phrase in (
        "A bets 100","B is all-in for 125","C calls 125","D is all-in for 200","E calls 200",
        "A now faces 100 more", "A may raise to at least 300","C faces only 75",
        "cannot re-raise","two short all-ins together make a full 100 increase",
        "venue's adopted rules and floor govern actual play"
    ):
        if phrase not in body:result.append("unsupported or missing: "+phrase)
    if body.count('href="'+RULE+'"')!=1:result.append("missing official primary source")
    if chr(0x2014) in body or "<script" in body or "solver-approved" in body:
        result.append("invalid content")
    return result

class Rule49PlayerSpecificTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=SOURCE.read_text(encoding="utf-8")
        cls.public=PUBLISHED.read_text(encoding="utf-8")
        cls.bsrc=BET_SOURCE.read_text(encoding="utf-8")
        cls.bpub=BET_PUBLISHED.read_text(encoding="utf-8")

    def test_independent_contribution_thresholds(self):
        full=100
        first=125-100
        second=200-125
        self.assertEqual((first,second),(25,75))
        self.assertTrue(first<full and second<full)
        self.assertEqual(first+second,full)
        self.assertEqual(200-100,100)  # A faces a complete increase since betting
        self.assertEqual(200+full,300) # minimum total if A raises
        self.assertEqual(200-125,75)   # C acted at 125
        self.assertEqual(125+full,225) # threshold for C to be reopened

    def test_primary_rules_reference_and_original_page_skeleton(self):
        for page in (self.src,self.public):
            self.assertEqual(errors(page),[])
            self.assertEqual(Links(page).ids.count("reopening-per-player"),1)
            self.assertEqual(page.count("After A calls 200, may C re-raise after calling 125 earlier?"),1)
            self.assertIn("The same wager can give different players different options.",page)
        self.assertEqual(example(self.src),example(self.public))
        self.assertEqual(self.src.count("<h2 "),8)
        self.assertEqual(self.public.count("<h2 "),9)
        self.assertIn('id="raise-example"',self.src)
        self.assertIn('id="self-check"',self.src)
        self.assertNotIn(chr(0x2014),self.src)

    def test_betting_primer_links_exactly_once_to_this_example(self):
        for page in (self.bsrc,self.bpub):
            self.assertEqual(Links(page).hrefs.count(DEST),1)
            self.assertIn("Multiple short all-ins can change that result.",page)
            self.assertIn("TDA rules 45 and 49",page)
        fragment='The <a href="'+DEST+'">player-by-player reopening example</a>'
        self.assertIn(fragment,self.bsrc)
        self.assertIn(fragment,self.bpub)

    def test_article_date_revision_not_false_external_source_recheck(self):
        manifest=json.loads((ROOT/"_source/pages.json").read_text(encoding="utf-8"))
        rules=next(p for p in manifest if p["path"]=="/poker/poker-rules-and-fair-play/")
        self.assertEqual((rules["date"],rules["updated"]),("2026-10-08","2026-11-20"))
        for required in (
            'article:published_time" content="2026-10-08"',
            'article:modified_time" content="2026-11-20"',
            '"datePublished": "2026-10-08"','"dateModified": "2026-11-20"',
            'Updated <time datetime="2026-11-20">November 20, 2026</time>',
        ):
            self.assertIn(required,self.public)
        self.assertIn("earlier October 16 rules-directory review",self.src)
        root=ET.fromstring((ROOT/"sitemap.xml").read_text(encoding="utf-8"))
        rows=[r for r in root if r.findtext("{*}loc")=="https://nolankido.com/poker/poker-rules-and-fair-play/"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0].findtext("{*}lastmod"),"2026-11-20")
        betting=next(p for p in manifest if p["path"]=="/poker/betting-and-pots/")
        self.assertEqual((betting["date"],betting["updated"]),("2026-10-05","2026-10-05"))

    def test_wrong_raise_rights_or_untrusted_source_are_detected(self):
        mutations=(
            self.src.replace("C faces only 75","C faces 100",1),
            self.src.replace("cannot re-raise","may re-raise",1),
            self.src.replace("raise to at least 300","raise to 200",1),
            self.src.replace('href="'+RULE+'"','href="https://example.invalid/"',1),
            self.src.replace('id="reopening-per-player"','id="removed"',1),
        )
        for changed in mutations:
            with self.subTest(change=changed!=self.src):
                self.assertNotEqual(changed,self.src)
                self.assertTrue(errors(changed) or Links(changed).ids.count("reopening-per-player")!=1)

    def test_registered_offline_without_user_authored_actions(self):
        runner=(ROOT/"_scripts/local_release_checks.py").read_text(encoding="utf-8")
        self.assertIn("test_turn56_tda_reopening.py",runner)
        folder=ROOT/".github/workflows"
        self.assertFalse(folder.exists() and any(p.is_file() and p.suffix in (".yml",".yaml") for p in folder.iterdir()))

if __name__=="__main__":
    unittest.main()
