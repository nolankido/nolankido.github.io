"""Reverse only this release's reviewed additions for older golden contracts.

No historical digest is refreshed. The independent test_ai_task_choice contract
also pins the actual pre-release inputs and checks the complete new behaviour.
"""
from pathlib import Path
import answer_review_history
import search_entry_history
import json,re
import beginner_history
import preflop_history
import flop_history
import river_history
import learning_path_history
import ranges_history
import betting_history
import checkpoint_history
import productivity_history
import holdem_essay_history
import uncertainty_history
import comics_history
import getting_started_history
import tournament_budget_history
import thunder_valley_history
import multiway_history
import short_stack_history
import poker_routes_history
import poker_course_history
import poker_practice_history
ROOT=Path(__file__).resolve().parents[1]
ROUTE='/technology/should-i-use-ai/'
NEW_SOURCES={'_source/ai-task-choice.json','_source/technology/should-i-use-ai.html',answer_review_history.SOURCE} | search_entry_history.NEW_SOURCES | set(beginner_history.change()['new_files']) | set(preflop_history.change()['new_files']) | set(flop_history.change()['new_files']) | set(river_history.change()['new_files']) | set(learning_path_history.change()['new_files']) | set(ranges_history.change()['new_files'])
NEW_OUTPUT='technology/should-i-use-ai/index.html'
NEW_SOURCES |= set(betting_history.change()['new_files']) | set(checkpoint_history.change()['new_files']) | set(productivity_history.change()['new_files'])
NEW_OUTPUTS={NEW_OUTPUT,answer_review_history.OUTPUT,beginner_history.OUTPUT,preflop_history.OUTPUT,flop_history.OUTPUT,river_history.OUTPUT,ranges_history.OUTPUT,betting_history.OUTPUT,checkpoint_history.OUTPUT,productivity_history.OUTPUT}
NEW_SOURCES |= set(holdem_essay_history.change()['new_files'])
NEW_OUTPUTS.add(holdem_essay_history.OUTPUT)
NEW_SOURCES |= set(uncertainty_history.change()['new_files'])
NEW_OUTPUTS.add(uncertainty_history.OUTPUT)
NEW_SOURCES |= set(comics_history.change()['new_files'])
NEW_OUTPUTS |= set(comics_history.change()['new_outputs'])
NEW_SOURCES |= set(getting_started_history.change()['new_files'])
NEW_OUTPUTS |= set(getting_started_history.change()['new_outputs'])
NEW_SOURCES |= set(tournament_budget_history.change()['new_files'])
NEW_OUTPUTS |= set(tournament_budget_history.change()['new_outputs'])
NEW_SOURCES |= set(thunder_valley_history.change()['new_files'])
NEW_OUTPUTS |= set(thunder_valley_history.change()['new_outputs'])
NEW_SOURCES |= set(multiway_history.change()['new_files'])
NEW_OUTPUTS |= set(multiway_history.change()['new_outputs'])
NEW_SOURCES |= set(short_stack_history.change()['new_files'])
NEW_SOURCES |= set(poker_routes_history.change()['new_files'])
NEW_SOURCES |= set(poker_course_history.change()['new_files'])
NEW_SOURCES |= set(poker_practice_history.change()['new_files'])
NEW_OUTPUTS |= set(poker_practice_history.change()['new_outputs'])
NEW_OUTPUTS |= set(poker_course_history.change()['new_outputs'])
NEW_OUTPUTS |= set(short_stack_history.change()['new_outputs'])

def before(path,data):
    data=answer_review_history.before(path,data)
    path=str(path)
    binary=isinstance(data,bytes)
    if not (path.endswith('.html') or path in {'_source/pages.json','technology/feed.xml','writing.xml','sitemap.xml'}):return data
    text=data.decode() if binary else data
    text=text.replace('  <link rel="icon" href="/favicon.png" type="image/png" sizes="96x96">\n','')
    text=text.replace('  <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">\n','')
    text=re.sub(r'<!-- AI task choice: start -->\n.*?<!-- AI task choice: end -->\n','',text,flags=re.S)
    if path=='_source/pages.json':
        text=json.dumps([p for p in json.loads(text) if p['id']!='ai-task-choice'],indent=2,ensure_ascii=False)+'\n'
    if path in {'technology/feed.xml','writing.xml'}:
        text=re.sub(r'    <item>.*?</item>\n',lambda m:'' if '<link>https://nolankido.com'+ROUTE+'</link>' in m[0] else m[0],text,flags=re.S)
    if path=='sitemap.xml':
        text=re.sub(r'  <url>.*?</url>\n',lambda m:'' if '<loc>https://nolankido.com'+ROUTE+'</loc>' in m[0] else m[0],text,flags=re.S)
    if path=='notes/index.html':
        text=re.sub(r'<article class="note-entry technology-publication">.*?</article>',lambda m:'' if 'href="'+ROUTE+'"' in m[0] else m[0],text,flags=re.S)
    if path=='find/index.html':
        old=text
        text=re.sub(r'<li class="find-item".*?</li>',lambda m:'' if 'href="'+ROUTE+'"' in m[0] else m[0],text,flags=re.S)
        if text!=old:
            text=text.replace('id="browse-technology"><summary>Technology <span class="find-group-count" hidden>(9)</span>', 'id="browse-technology"><summary>Technology <span class="find-group-count" hidden>(8)</span>')
    return text.encode() if binary else text

def read(path):return before(path,(ROOT/path).read_bytes())
