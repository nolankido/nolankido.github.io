"""Evaluate declared regression targets against the real committed Poker index.

No network, learner records, paid services or claim of independent human grading.
The legacy scorer reproduces the exact frozen ranking formula and constants.
"""
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '_tests'))
import poker_search_titles_history as title_history
import poker_study_list_history as study_history
import poker_progress_history as progress_history
FOLDER = Path('_reports/poker-search-intent')
BASE = '1d6afff35e16d74a04415f8bc85dafe6f5b369bd'
LEGACY_SHA = 'c8ad7e80e8f0d9be0a13421c2f2c45beb6744e6f447a70a08ea36c83628df987'


def snapshot_text(root, path):
    try:
        return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=root,
                                       stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError:
        # A shallow checkout can lack the parent commit. Reverse only the exact
        # reviewed delta and verify both hashes; never fetch or guess old text.
        delta = json.loads((root / '_tests/poker-search-change.json').read_text())
        if delta['commit'] != BASE: raise ValueError('Wrong snapshot reconstruction')
        item = delta['paths'][path]
        raw = title_history.before(path, (root / path).read_bytes())
        if sha256(raw).hexdigest() != item['new_sha256']:
            raise ValueError('Cannot reconstruct a snapshot from changed bytes: ' + path)
        text = raw.decode()
        for edit in reversed(item['edits']):
            if text[edit['start']:edit['end']] != edit['new']:
                raise ValueError('Snapshot edit does not match')
            text = text[:edit['start']] + edit['old'] + text[edit['end']:]
        if sha256(text.encode()).hexdigest() != item['old_sha256']:
            raise ValueError('Reconstructed snapshot hash does not match')
        return text


class Cards(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.rows = []; self.card = None; self.passage = None; self.title = False
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'article' and 'data-finder-card' in a:
            self.card = {'id': a['data-id'], 'kind': a['data-kind'], 'text': a['data-search'],
                         'title': '', 'passages': [], 'index': len(self.rows)}
            if 'data-search-title' in a: self.card['searchTitle'] = a['data-search-title']
        elif self.card is not None:
            if tag == 'h3': self.title = True
            if tag == 'a' and self.title: self.card['url'] = a['href']
            if tag == 'p' and 'data-finder-passage' in a:
                self.passage = {'anchor': a['data-anchor'], 'heading': a['data-heading'], 'text': ''}

    def handle_data(self, text):
        if self.card is not None and self.title: self.card['title'] += text
        if self.passage is not None: self.passage['text'] += text

    def handle_endtag(self, tag):
        if tag == 'h3': self.title = False
        if tag == 'p' and self.passage is not None:
            self.card['passages'].append(self.passage); self.passage = None
        if tag == 'article' and self.card is not None:
            self.card['body'] = ' '.join(p['heading'] + ' ' + p['text'] for p in self.card['passages'])
            self.rows.append(self.card); self.card = None


ENGINE = r'''
const fs=require('node:fs'),vm=require('node:vm');
const {rows,cases,legacy,script}=JSON.parse(fs.readFileSync(0,'utf8'));
let engine;
if(legacy){
 const start=legacy.indexOf('  const normalize ='),end=legacy.indexOf('  const cards =');
 if(start<0||end<start)throw Error('Legacy source boundaries changed');
 const ctx={module:{exports:{}}};
 vm.runInNewContext(legacy.slice(start,end)+`
 function plan(value){const query=normalize(value.slice(0,160).replace(/c[ -]bet/gi,'cbet')).split(/\\s+/).filter(word=>word&&!stop.has(word));return {query,groups:query.map(word=>aliases[word]||[word])};}
 function score(card,p){if(!p.groups.every(g=>g.some(t=>includes(card.text+' '+card.body,t))))return -1;return p.groups.reduce((n,g)=>n+(g.some(t=>includes(card.title,t))?20:g.some(t=>includes(card.text,t))?5:1),0)+(p.query.length&&card.title===p.query.join(' ')?50:0);}
 function passage(card,p){const selected=card.passages.map((s,index)=>({s,index,score:p.groups.reduce((n,g)=>n+(g.some(t=>includes(normalize(s.text+' '+s.heading),t))?1:0),0)})).sort((a,b)=>b.score-a.score||a.index-b.index)[0];return p.groups.length&&selected&&selected.score>0?selected.s:null;}
 module.exports={normalize,plan,score,passage};`,ctx);
 engine=ctx.module.exports;
}else if(script){const ctx={module:{exports:{}}};vm.runInNewContext(script,ctx);engine=ctx.module.exports;}
else engine=require('./assets/poker-finder.js');
const cards=engine.prepare?rows.map(engine.prepare):rows.map(r=>({...r,title:engine.normalize(r.title),text:engine.normalize(r.text),body:engine.normalize(r.body)}));
const result=cases.map(c=>{const p=engine.plan(c.query);const found=cards.map(card=>({card,score:engine.score(card,p)})).filter(x=>x.score>=0).sort((a,b)=>b.score-a.score||a.card.index-b.card.index);return {id:c.id,query:c.query,matches:found.length,hit_top_three:found.slice(0,3).some(x=>c.acceptable_paths.includes(x.card.url)),top_three:found.slice(0,3).map(x=>{const s=engine.passage(x.card,p);return {url:x.card.url,score:x.score,section:s&&s.anchor?x.card.url+'#'+s.anchor:null,excerpt:s?s.text.slice(0,320):null};})};});
process.stdout.write(JSON.stringify(result));
'''


def evaluate(root=ROOT, baseline=False, prior_release=False, titles_release=False, study_list_release=False):
    if sum((baseline, prior_release, titles_release, study_list_release)) > 1:
        raise ValueError('Choose one historical release')
    queries = json.loads((root / FOLDER / 'queries.json').read_text())
    cases = queries['cases']
    if len(cases) != 30 or len({c['id'] for c in cases}) != 30 or any(not c['reason'] or not c['acceptable_paths'] for c in cases):
        raise ValueError('Keep 30 distinct declared targets with relevance reasons')
    index_text = snapshot_text(root, 'poker/find/index.html') if baseline else (root / 'poker/find/index.html').read_text()
    script = (root / 'assets/poker-finder.js').read_text()
    if study_list_release:
        index_text = progress_history.before('poker/find/index.html', index_text)
        script = progress_history.before('assets/poker-finder.js', script)
    if titles_release:
        index_text = study_history.before('poker/find/index.html', index_text)
        script = study_history.before('assets/poker-finder.js', script)
    if prior_release:
        index_text = title_history.before('poker/find/index.html', index_text)
        script = title_history.before('assets/poker-finder.js', script)
    rows = Cards(index_text).rows
    destinations = {r['url'] for r in rows}
    for case in cases:
        if not all(p in destinations for p in case['acceptable_paths']):
            raise ValueError('No actual destination for ' + case['id'])
    legacy = snapshot_text(root, 'assets/poker-finder.js') if baseline else None
    if legacy and sha256(legacy.encode()).hexdigest() != LEGACY_SHA:
        raise ValueError('Legacy formula is not the frozen source')
    result = subprocess.run(['node', '-e', ENGINE], cwd=root,
                            input=json.dumps({'rows': rows, 'cases': cases, 'legacy': legacy, 'script': script if prior_release or titles_release or study_list_release else None}),
                            text=True, capture_output=True, check=True)
    results = json.loads(result.stdout)
    return {'scope': queries['status'], 'baseline_commit': BASE,
            'query_sha256': sha256((root / FOLDER / 'queries.json').read_bytes()).hexdigest(),
            'index_sha256': sha256(index_text.encode()).hexdigest(),
            'script_sha256': LEGACY_SHA if baseline else sha256(script.encode()).hexdigest(),
            'entries': len(rows), 'target_hits_top_three': sum(c['hit_top_three'] for c in results),
            'total_queries': len(results), 'results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--prior-release', action='store_true', help='Replay the frozen 29/30 release')
    parser.add_argument('--titles-release', action='store_true', help='Replay the frozen 30/30 title-ranking release')
    parser.add_argument('--study-list-release', action='store_true', help='Replay the frozen study-list release')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = evaluate(baseline=args.baseline, prior_release=args.prior_release, titles_release=args.titles_release, study_list_release=args.study_list_release)
    if args.write:
        if args.baseline or args.prior_release:
            target = ROOT / FOLDER / ('baseline.json' if args.baseline else 'results.json')
        elif args.titles_release:
            target = ROOT / '_reports/poker-search-titles/results.json'
        elif args.study_list_release:
            target = ROOT / '_reports/poker-study-list/search-results.json'
        else:
            target = ROOT / '_reports/poker-progress/search-results.json'
        text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if (args.baseline or args.prior_release or args.titles_release or args.study_list_release) and target.exists() and target.read_text() != text:
            raise ValueError('The frozen baseline would change; use a separately labeled evaluation round')
        target.write_text(text)
    print(str(report['target_hits_top_three']) + '/30 declared targets in the first three results')
    for row in report['results']:
        print(row['id'], 'hit' if row['hit_top_three'] else 'MISS', row['query'], [r['url'] for r in row['top_three']])
