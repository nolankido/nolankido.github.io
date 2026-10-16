"""Independent ledger checks and branching rules, not a strategy score."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import unittest
from test_site import ROOT, build
import poker_round_practice as practice
import poker_finder
import check_live
import round_practice_history as history


def node(code, data):
    r = subprocess.run(['node','-e',"const h=require('./assets/poker-round-practice.js');const data=JSON.parse(require('fs').readFileSync(0,'utf8'));"+code],input=json.dumps(data),text=True,capture_output=True,cwd=ROOT,timeout=30)
    if r.returncode: raise AssertionError(r.stderr)
    return json.loads(r.stdout)


TRACE = """let s=h.start(data.state),out=[];for(const [action,add] of data.moves){const old=JSON.stringify(s),r=h.act(s,action,add);if(old!==JSON.stringify(s))throw Error('Input mutated');out.push({...r,pot:h.pot(r.state)});if(r.ok)s=r.state;}process.stdout.write(JSON.stringify(out));"""


class RoundPracticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=practice.load(ROOT)
        cls.cases={c['id']:c for c in cls.data['cases']}
        cls.outputs=build.build_outputs()

    def trace(self, case, moves):
        return node(TRACE,{'state':self.cases[case]['state'],'moves':moves})

    def test_release_preserves_every_previous_byte_through_only_its_frozen_delta(self):
        b=json.loads((ROOT/'_tests/round-practice-baseline.json').read_text())
        self.assertEqual((b['commit'],len(b['pages']),len(b['outputs']),len(b['files'])),('aa81b7f310c3d5fd23f70e7eae10066dffb604de',193,221,472))
        self.assertEqual(history.pages(build.public_pages()),b['pages'])
        old=history.outputs(self.outputs)
        self.assertEqual(set(map(str,old)),set(b['outputs']))
        for p,text in old.items():self.assertEqual(sha256(text.encode()).hexdigest(),b['outputs'][str(p)],str(p))
        for p,digest in {**b['files'],**b['extras']}.items():self.assertEqual(sha256(history.before(p,(ROOT/p).read_bytes())).hexdigest(),digest,p)
        actual={p.relative_to(ROOT).as_posix() for d in ['_source','_scripts','assets','downloads'] for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(history.files(actual),set(b['files']))
        self.assertEqual(set(history.change()['new_files']),{practice.DATA,practice.CSS,practice.SCRIPT,'_scripts/poker_round_practice.py'})
        self.assertEqual(history.change()['new_outputs'],{})
        for p in [practice.DATA,'_scripts/build.py','_source/poker/free-poker-learning-path.html','poker/free-poker-learning-path/index.html']:
            raw=(ROOT/p).read_bytes()+b'Unreviewed';self.assertEqual(history.before(p,raw),raw)

    def test_three_worked_lines_have_independently_counted_ledgers(self):
        expected={'preflop':([5,6,6],[[2,1,2],[2,2,2],[2,2,2]]),'flop':([6,10,14,18],[[0,0,0],[0,0,4],[4,0,4],[4,4,4]]),'raise':([26],[[0,10,10]])}
        for key,case in self.cases.items():
            r=self.trace(key,[(w['action'],w['add']) for w in case['worked']])
            self.assertTrue(all(x['ok'] for x in r))
            self.assertEqual([x['actor'] for x in r],[w['actor'] for w in case['worked']])
            self.assertEqual([x['pot'] for x in r],expected[key][0])
            self.assertEqual([[p['paid'] for p in x['state']['players']] for x in r],expected[key][1])
            self.assertEqual(r[-1]['state']['ending']['kind'],'round')

    def test_equal_blind_contributions_do_not_remove_the_big_blind_option(self):
        r=self.trace('preflop',[('call',2),('call',1),('raise',4),('call',4),('call',4)])
        self.assertEqual(r[1]['state']['pending'],['big']);self.assertIsNone(r[1]['state']['ending'])
        self.assertEqual(r[2]['state']['pending'],['button','small']);self.assertEqual(r[2]['state']['lastRaise'],4)
        self.assertEqual(r[-1]['pot'],18);self.assertEqual(r[-1]['state']['ending']['next'],'flop')

    def test_a_late_bet_and_raise_revisit_players_who_already_acted(self):
        r=self.trace('flop',[('check',0),('check',0),('bet',5),('call',5),('raise',13),('call',8),('call',8)])
        self.assertTrue(all(x['ok'] for x in r));self.assertEqual(r[2]['state']['pending'],['small','big'])
        self.assertEqual(r[4]['state']['pending'],['button','small']);self.assertEqual(r[4]['state']['lastRaise'],8)
        self.assertIsNone(r[5]['state']['ending']);self.assertEqual(r[-1]['pot'],45)
        self.assertEqual(r[-1]['state']['ending']['next'],'turn')

    def test_full_raise_uses_the_increment_and_input_is_extra_counters(self):
        r=self.trace('raise',[('raise',6),('raise',11),('raise',12),('call',6)])
        self.assertEqual([x['ok'] for x in r],[False,False,True,True])
        self.assertEqual(r[2]['state']['current'],16);self.assertEqual(r[2]['state']['lastRaise'],6)
        self.assertEqual(r[-1]['pot'],38)
        r=self.trace('raise',[('call',10),('call',6)])
        self.assertEqual(r[0]['code'],'call-cost');self.assertEqual(r[-1]['pot'],26)

    def test_folds_keep_prior_payments_and_return_uncalled_counters_separately(self):
        r=self.trace('raise',[('fold',0)])[-1]
        self.assertEqual(r['state']['ending'],{'kind':'fold','winner':'big','returned':6,'awarded':14})
        self.assertEqual(r['pot'],20)
        r=self.trace('flop',[('bet',4),('fold',0),('fold',0)])[-1]
        self.assertEqual(r['state']['ending'],{'kind':'fold','winner':'small','returned':4,'awarded':6})
        r=self.trace('preflop',[('fold',0),('fold',0)])[-1]
        self.assertEqual(r['state']['ending'],{'kind':'fold','winner':'big','returned':1,'awarded':2})

    def test_invalid_moves_leave_the_ledger_and_pending_decisions_unchanged(self):
        for key,moves,codes in [('preflop',[('check',0),('bet',2),('call',1),('call',2.5)],['check-facing','bet-existing','call-cost','amount']),('flop',[('raise',4),('call',0),('fold',0),('bet',1)],['raise-none','call-zero','fold-free','minimum'])]:
            r=self.trace(key,moves)
            self.assertEqual([x['code'] for x in r],codes)
            for item in r:self.assertEqual(item['state'],{**self.cases[key]['state'],'ending':None})
        r=self.trace('flop',[('bet',1000),('raise',1001),('call',1000),('call',1000),('check',0)])
        self.assertFalse(r[1]['ok']);self.assertEqual(r[-2]['pot'],3006);self.assertEqual(r[-1]['code'],'closed')

    def test_reachable_rounds_obey_conservation_and_completion_invariants(self):
        # Seeded branch exploration checks accounting and completion independently.
        result=node("""let n=0,ended=0,seed=314159;function rnd(){seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;}for(const c of data){for(let j=0;j<160;j++){let s=h.start(c.state),previous=h.pot(s);for(let k=0;k<30&&!s.ending;k++){const p=s.players.find(x=>x.id===s.pending[0]),owed=s.current-p.paid,actions=owed?['call','raise','fold']:s.current?['check','raise']:['check','bet'];let a=actions[Math.floor(rnd()*actions.length)],add=a==='call'?owed:a==='bet'?2+Math.floor(rnd()*8):a==='raise'?s.current+s.lastRaise-p.paid+Math.floor(rnd()*8):0;const r=h.act(s,a,add);if(!r.ok)continue;const z=r.state;if(h.pot(z)!==previous+add)throw Error('Counter conservation');if(z.players.some((v,i)=>v.paid<s.players[i].paid))throw Error('Payment disappeared');if(z.pending.some(id=>z.players.find(p=>p.id===id).folded))throw Error('Folded turn');if(z.ending?.kind==='round' && (z.pending.length||new Set(z.players.filter(p=>!p.folded).map(p=>p.paid)).size!==1))throw Error('Premature round end');if(z.ending?.kind==='fold' && (z.players.filter(p=>!p.folded).length!==1||z.ending.awarded+z.ending.returned!==h.pot(z)))throw Error('Bad settlement');s=z;previous=h.pot(s);n++;}if(s.ending)ended++;}}process.stdout.write(JSON.stringify({n,ended}));""",list(self.cases.values()))
        self.assertGreater(result['n'],1400);self.assertGreater(result['ended'],400)

    def test_malformed_starting_states_are_rejected(self):
        bad=[None,{}]
        for mutate in [lambda s:s['players'].pop(),lambda s:s['pending'].append('button'),lambda s:s.update(current=5),lambda s:s['players'][0].update(paid=-1),lambda s:s['players'][0].update(folded=True),lambda s:s.update(pending=['small','big']),lambda s:s.update(lastRaise=1)]:
            s=deepcopy(self.cases['preflop']['state']);mutate(s);bad.append(s)
        self.assertEqual(node("let rejected=0;for(const s of data)try{h.start(s);}catch(e){rejected++;}process.stdout.write(JSON.stringify(rejected));",bad),len(bad))

    def test_course_links_search_and_live_checks_include_the_actual_exercise(self):
        page=self.outputs[build.output_path(practice.ROUTE)]
        for case in self.cases:self.assertIn('id="round-practice-'+case+'"',page)
        for slug,case in [('first-decisions','preflop'),('starting-hand-decisions','preflop'),('first-flop-decisions','flop')]:
            self.assertIn(practice.ROUTE+'#round-practice-'+case,self.outputs[build.output_path('/poker/'+slug+'/')])
        route=next(p for p in build.public_pages() if p['path']==practice.ROUTE)
        sections={s['anchor']:s['text'] for s in poker_finder.guide_sections(ROOT,route,poker_finder.poker_content.load(ROOT))}
        for key,c in self.cases.items():
            self.assertIn(c['prompt'],sections['round-practice-'+key])
            for worked in c['worked']:self.assertNotIn(worked['reason'],sections['round-practice-'+key])
        self.assertEqual(len(check_live.targets()),472)
        self.assertIn('/'+practice.CSS,check_live.targets());self.assertIn('/'+practice.SCRIPT,check_live.targets())
        self.assertNotIn('<form',practice.render(ROOT))
        script=(ROOT/practice.SCRIPT).read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest','localStorage','sessionStorage','document.cookie','innerHTML','sendBeacon','history.pushState','history.replaceState','location.assign','location.replace']:
            self.assertNotIn(forbidden,script)
        self.assertNotRegex(script,r'\blocation\.hash\s*=(?!=)')


if __name__=='__main__':unittest.main()
