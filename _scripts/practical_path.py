"""Connect existing practical AI resources into one native, private-use path."""
from copy import deepcopy
from hashlib import sha256
from html import escape
from pathlib import Path
import re

BEGIN = '<!-- Practical AI path: start -->'
END = '<!-- Practical AI path: end -->'
CSS = Path('assets/practical-ai-path.css')
WORKBOOK = Path('downloads/practical-ai-workbook.txt')
SEO_TITLE = 'Practical AI Projects | AI Works Human Decides | Nolan Kido'
DESCRIPTION = "Explore Nolan Kido's practical AI projects: local review replies, book continuity checks, and a cooking-planner simulation. AI Works Human Decides guides the work."
STAGES = (
    ('ai-task-choice', 'Decide', 'Decide whether AI fits the task', 'Check the purpose, permitted inputs, consequences and a simpler alternative before starting.', 'A decision to pause, use a simpler method, prepare first or try a bounded draft.', 'should-i-use-ai.txt'),
    ('task-brief', 'Brief', 'Write a brief with a finish line', 'Name the useful result, supplied material, boundaries and checks before delegating production.', 'A written brief that keeps assumptions, permissions and responsibilities visible.', 'ai-task-brief.txt'),
    ('ai-answer-review', 'Check', 'Check the answer against evidence', 'Choose checks for facts, numbers, summaries, writing, code or advice. Follow the source-review example when the task is a summary.', 'An evidence record for the consequential claims, with untested parts still visible.', 'ai-answer-review.txt'),
    ('ai-time-savings', 'Measure', 'Compare the whole cost of the task', 'Count preparation, production, review, repairs, setup and upkeep at the same acceptable quality.', 'A time comparison and a choice to keep, adjust, stop or gather more observations.', 'workflow-time-review.txt'),
)


def records(pages, root):
    by_id = {p['id']: p for p in pages}
    result = []
    for key, short, title, purpose, output, sheet in STAGES:
        p = by_id.get(key)
        if not p or p.get('noindex') or not p['path'].startswith('/technology/'):
            raise ValueError('Practical AI path needs its published, indexable destination: ' + key)
        content = (root / 'downloads' / sheet).read_text(encoding='utf-8')
        if not content.strip() or not content.endswith('\n'):
            raise ValueError('Practical AI path needs complete original blank worksheets')
        result.append({'id': key, 'short': short, 'title': title, 'purpose': purpose,
                       'output': output, 'path': p['path'], 'sheet': sheet, 'content': content})
    return result


def metadata(pages):
    result = deepcopy(pages)
    for p in result:
        if p['id'] == 'technology':
            p.update(seo_title=SEO_TITLE, description=DESCRIPTION)
    return result


def workbook(pages, root):
    entries = records(pages, root)
    text = ('ONE TASK, FOUR USEFUL CHECKPOINTS\n'
            'Nolan Kido | https://nolankido.com/technology/#practical-ai-path\n\n'
            'Keep a completed copy privately in your own notes. This file combines\n'
            'four existing blank worksheets, unchanged, for one task. Use only the\n'
            'sections you need. A simpler method or a decision to stop is a valid end.\n'
            'No AI runs in these tools. Completing the file certifies nothing.\n\n'
            'TASK RECORD\nTask name and date:\nUseful finished result:\n'
            'Source material and version (references, not confidential copies):\n'
            'Person responsible for the final decision:\n\n')
    for i, e in enumerate(entries, 1):
        text += ('=' * 64 + '\n' + str(i) + '. ' + e['short'].upper() + '\n'
                 'Guide: https://nolankido.com' + e['path'] + '\n'
                 'Original blank worksheet: https://nolankido.com/downloads/' + e['sheet'] + '\n'
                 + '=' * 64 + '\n\n' + e['content'] + '\n')
    text += ('FINAL TASK DECISION\nWhat I will actually use:\n'
             'What remains unverified or needs another person:\n'
             'Keep / adjust / stop / gather more observations:\n'
             'Reason and next review point:\n\n'
             'A faithful summary can preserve an inaccurate source. Correct arithmetic\n'
             'can use wrong inputs. A reviewed draft is not permission to send or\n'
             'publish. Estimates are not observed results, and a before/after change\n'
             'alone does not show that AI caused it. Keep those limits with the record.\n')
    return text


def marked(text):
    return BEGIN + '\n' + text + '\n' + END + '\n'


def body(page, content, pages, root):
    if page['id'] == 'resources':
        link = marked('<h3 id="practical-ai-workbook-resource">One task, one private record.</h3><p><a href="/technology/#practical-ai-path">Follow the Decide / Brief / Check / Measure path</a>, or <a href="/downloads/practical-ai-workbook.txt" download>save the complete blank workbook (.txt)</a>. The four existing worksheets are combined unchanged, with links to their guides. You can <a href="/technology/#practical-ai-workbook">read the whole workbook here</a> before downloading.</p>')
        anchor = '<h3 id="workflow-resource-title">'
        if anchor not in content: raise ValueError('Practical AI path needs the existing resource panel')
        return content.replace(anchor, link + anchor, 1)
    if page['id'] != 'technology': return content
    entries = records(pages, root)
    section = '<section class="section folio-row ai-path" id="practical-ai-path" aria-labelledby="practical-ai-path-title"><div class="section-meta"><p class="section-label">One task / Four useful checkpoints</p></div><div class="section-content"><h2 class="section-title" id="practical-ai-path-title">Decide. Brief. Check. Measure.</h2><p class="section-deck">Start with one task you want to make easier. Use the stages you need, then decide whether the result is worth keeping. A simpler method or a decision to stop is a valid endpoint.</p><ol class="ai-path-steps">'
    for i, e in enumerate(entries, 1):
        section += '<li><p class="ai-path-label">' + str(i).zfill(2) + ' / ' + e['short'] + '</p><h3><a href="' + e['path'] + '">' + escape(e['title']) + '</a></h3><p>' + escape(e['purpose']) + '</p><p class="ai-path-output"><strong>What you keep:</strong> ' + escape(e['output']) + '</p></li>'
    section += '</ol><p class="small-copy">These are thinking aids and browser tools. No AI runs here, and following the path does not certify accuracy, safety or time savings. For a summary, <a href="/technology/check-ai-summary/">inspect the source-to-summary worked example</a>; other answers need checks suited to their use.</p><div class="ai-workbook" id="practical-ai-workbook"><h3>Keep the four stages in one private workbook.</h3><p>Save one text file for the task, its brief, the checks and the full time cost. It combines the four original blank worksheets unchanged and links to each guide. Complete your copy in your own notes; this website does not collect it.</p><p><a class="button" href="/downloads/practical-ai-workbook.txt" download>Save the complete workbook (.txt)</a></p><details><summary>Read the complete blank workbook before downloading</summary><pre>' + escape(workbook(pages, root)) + '</pre></details></div></div></section>'
    # Replace the two older isolated promotions with one coherent path. Keep
    # their existing sources intact, and independently protect them in history.
    for name in ('AI task choice', 'AI answer review'):
        pattern = r'<!-- ' + name + r': start -->\n.*?<!-- ' + name + r': end -->\n'
        content, n = re.subn(pattern, '', content, count=1, flags=re.S)
        if n != 1: raise ValueError('Practical AI path needs the existing reviewed promotion: ' + name)
    anchor = '<section class="section folio-row" aria-labelledby="working-examples">'
    if anchor not in content: raise ValueError('Practical AI path needs the existing working examples')
    return content.replace(anchor, marked(section) + anchor, 1)


def schema(page, content, pages, root, origin):
    if page['id'] != 'technology': return content
    result = deepcopy(content)
    entries = records(pages, root)
    result['mainEntity'] = {'@type': 'ItemList', '@id': origin + '/technology/#practical-ai-path',
        'name': 'Decide. Brief. Check. Measure.', 'numberOfItems': len(entries),
        'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': e['title'], 'url': origin + e['path']} for i, e in enumerate(entries, 1)]}
    return result


def head(page, root):
    if page['id'] != 'technology': return ''
    version = sha256((root / CSS).read_bytes()).hexdigest()[:12]
    return '\n  <link rel="stylesheet" href="/assets/practical-ai-path.css?v=' + version + '">'
