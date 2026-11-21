"""Turn 55: three published NolanPoker journeys from video to evidence to practice.

Source- and output-level checks only; cannot inspect live video or solver output.
"""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PAIRS=(
    ("_source/poker/home.html","poker/index.html"),
    ("_source/poker/portland-meadows-ep1.html","poker/episodes/portland-meadows-ep1/index.html"),
    ("_source/poker/portland-meadows-standoff.html","poker/episodes/portland-meadows-standoff/index.html"),
    ("_source/poker/reserve-day-1.html","poker/episodes/reserve-day-1/index.html"),
)
JOURNEYS=(
    ("qABaiIcvvpU","/poker/episodes/portland-meadows-ep1/#hand-64o-record",
     "/poker/six-to-ten-bb-tournament-decisions/#bridge-practice"),
    ("I75GOBVXij4","/poker/episodes/portland-meadows-standoff/#standoff-second-decision",
     "/poker/short-stack-decisions/#icm-call"),
    ("edNSD5BjIV8","/poker/episodes/reserve-day-1/#reserve-questions",
     "/poker/side-pot-lab/#all-in-action"),
)

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

class Anchors(HTMLParser):
    def __init__(self,html):
        super().__init__(convert_charrefs=True)
        self.ids=[]
        self.hrefs=[]
        self.feed(html)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):self.ids.append(a["id"])
        if tag=="a" and a.get("href"):self.hrefs.append(a["href"])

def video_card(hub,vid):
    target='https://www.youtube.com/watch?v='+vid
    marker='href="'+target+'"'
    begin=hub.find(marker)
    if begin<0:raise ValueError("missing featured video: "+vid)
    start=hub.rfind('<article class="poker-content-card"',0,begin)
    end=hub.find("</article>",begin)
    if start<0 or end<0:raise ValueError("missing bounded video card: "+vid)
    return hub[start:end+len("</article>")]

def journey_errors(hub,ep,stand,res):
    issues=[]
    episode={"qABaiIcvvpU":ep,"I75GOBVXij4":stand,"edNSD5BjIV8":res}
    for video,source,practice in JOURNEYS:
        card=video_card(hub,video)
        links=Anchors(card).hrefs
        if "https://www.youtube.com/watch?v="+video not in links:
            issues.append("video card no longer opens the verified upload")
        if source not in links:
            issues.append("video card lacks direct source-backed practice route: "+video)
        if practice not in Anchors(episode[video]).hrefs:
            issues.append("companion lacks distinct external practice: "+video)
        if video=="qABaiIcvvpU" and practice not in links:
            issues.append("Deepstack card lost its independent quiz shortcut")
    if hub.count('href="#nolanpoker-hand-study"')!=2:
        issues.append("original two hand-study hub shortcuts moved")
    if "not a solver verdict" not in ep.lower():
        issues.append("Deepstack's fictional practice boundary is absent")
    if "does not settle the reported A-K call" not in stand:
        issues.append("Stand Off fictional ICM cannot grade A-K")
    if "not from my Reserve hand" not in res:
        issues.append("Reserve fictional side-pot exercise lacks boundary")
    return issues

class NolanPokerAfterWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=[read(p[0]) for p in PAIRS]
        cls.generated=[read(p[1]) for p in PAIRS]

    def test_video_to_companion_to_separate_practice_routes(self):
        for pages in (self.sources,self.generated):
            self.assertEqual(journey_errors(*pages),[])
            hub,deepstack,stand,res=pages
            for video,_,_ in JOURNEYS:
                self.assertIn("https://www.youtube.com/watch?v="+video,Anchors(hub).hrefs)
            self.assertIn("/poker/episodes/portland-meadows-ep1/#hand-77-record",
                          Anchors(video_card(hub,"qABaiIcvvpU")).hrefs)
            self.assertIn("/poker/episodes/reserve-day-1/#reserve-pots",
                          Anchors(video_card(hub,"edNSD5BjIV8")).hrefs)
        for src,public in zip(self.sources,self.generated):
            self.assertNotIn(chr(0x2014),src)

    def test_exact_new_text_parity_in_built_and_manual_pages(self):
        markers=(
            '<article class="poker-content-card" id="nolanpoker-deepstack">',
            '<section id="hand-64o-record"',
            '<section id="standoff-second-decision"',
            '<section id="reserve-questions"',
        )
        for (source,published),marker in zip(zip(self.sources,self.generated),markers):
            self.assertIn(marker,source)
            self.assertIn(marker,published)
        required=(
            "try nine fictional short-stack questions",
            "try nine separate fictional questions",
            "Practice a separate fictional chip-versus-ICM call",
            "Build the main pot, side pot and unmatched refund",
        )
        for snippet,pair in zip(required,zip(self.sources,self.generated)):
            src,out=pair
            self.assertEqual(src.count(snippet),1)
            self.assertEqual(out.count(snippet),1)
        self.assertEqual(video_card(self.sources[0],"qABaiIcvvpU"),
                         video_card(self.generated[0],"qABaiIcvvpU"))

    def test_all_practice_fragments_exist_on_distinct_published_pages(self):
        for route in sorted({r[2] for r in JOURNEYS}|{
            "/poker/short-stack-decisions/#study-loop"
        }):
            local,fragment=route.split("#")
            page=read(local.lstrip("/")+"index.html")
            self.assertEqual(Anchors(page).ids.count(fragment),1,route)
        for _,source,practice in JOURNEYS:
            for url in (source,practice):
                local=url.split("#")[0]
                self.assertTrue((ROOT/local.lstrip("/")/"index.html").is_file())
        sitemap=ET.fromstring(read("sitemap.xml"))
        indexed={x.findtext("{*}loc") for x in sitemap}
        for _,source,practice in JOURNEYS:
            self.assertIn("https://nolankido.com"+source.split("#")[0],indexed)
            self.assertIn("https://nolankido.com"+practice.split("#")[0],indexed)

    def test_existing_six_video_gallery_and_publication_metadata_stay(self):
        hub=self.generated[0]
        videos=json.loads(read("_source/poker/nolanpoker-video-thumbnails.json"))["videos"]
        self.assertEqual(len(videos),6)
        video_gallery=hub.split('<section class="poker-public-video-list"',1)[1].split(
            '<section class="poker-video-source-note"',1)[0]
        self.assertEqual(len(re.findall('<article class="poker-content-card"',video_gallery)),6)
        for v in videos:
            self.assertEqual(Anchors(video_card(hub,v["video_id"])).hrefs.count(
                "https://www.youtube.com/watch?v="+v["video_id"]),1)
            self.assertIn(v["title"],hub)
        pages={p["path"]:p for p in json.loads(read("_source/pages.json"))}
        self.assertEqual(pages["/poker/"]["updated"],"2026-11-20")
        self.assertIn('"dateModified": "2026-11-20"',hub)
        self.assertEqual(pages["/poker/six-to-ten-bb-tournament-decisions/"]["updated"],"2026-11-18")
        for p in self.generated:
            self.assertNotIn("youtube.com/embed",p)

    def test_correction_gates_and_no_reviewer_approval_fabrication(self):
        for page in self.generated[1:]:
            self.assertIn("not",page)
        for src in self.sources:
            self.assertNotIn("solver-approved",src)
            self.assertNotIn("verified final cut",src.lower())
        self.assertIn("not a solver verdict",self.sources[1])
        self.assertIn("does not settle",self.sources[2])
        self.assertIn("not from my Reserve hand",self.sources[3])
        record=json.loads(read("downloads/portland-meadows-ep1-scene-claims.json"))
        self.assertIs(record["human_release_approval"],False)
        self.assertIs(record["current_public_cut_graphics_checked"],False)

    def test_negative_controls_identify_wrong_destinations_and_removed_scope(self):
        hub,deepstack,stand,res=self.generated
        samples=[
            (hub.replace('/poker/six-to-ten-bb-tournament-decisions/#bridge-practice',
                         '/poker/missing/#bridge-practice',1),deepstack,stand,res),
            (hub,deepstack,stand.replace("does not settle the reported A-K call",
                                        "proves the reported A-K call",1),res),
            (hub,deepstack,stand,res.replace("not from my Reserve hand",
                                            "exactly from my Reserve hand",1)),
        ]
        for row in samples:
            self.assertTrue(journey_errors(*row))

    def test_local_release_group_without_ci(self):
        runner=read("_scripts/local_release_checks.py")
        self.assertIn("test_turn55_video_to_practice.py",runner)
        actions=ROOT/".github/workflows"
        self.assertFalse(actions.exists() and any(
            x.is_file() and x.suffix.lower() in (".yml",".yaml") for x in actions.iterdir()
        ))

if __name__=="__main__":
    unittest.main()
