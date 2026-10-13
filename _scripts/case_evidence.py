"""Link the existing historical case to its immutable public release evidence."""
from html import escape
import json
import re

PAGE_ID = 'ai-website-verification'
PATH = 'technology/checking-ai-website-changes/index.html'
BEGIN = '<!-- Historical case sources: start -->'
END = '<!-- Historical case sources: end -->'
ANCHOR = '<details><summary>Inspect the release identifiers and evidence scope</summary>'
REPO = 'https://github.com/nolankido/nolankido.github.io'


def block(root):
    record = json.loads((root / 'downloads/website-check-evidence.json').read_text())
    old, new = record['pre_repair']['commit'], record['repaired']['candidate']
    run = record['repaired']['run']
    if not all(re.fullmatch(r'[0-9a-f]{40}', sha) for sha in (old, new)) or type(run) is not int or run <= 0:
        raise ValueError('Historical source links require full commit IDs and a workflow run ID')
    links = (
        (REPO + '/compare/' + old + '...' + new, 'Compare the actual repair',
         'See the extra closing tag removed from the source and generated page, alongside the changes to the checks.'),
        (REPO + '/actions/runs/' + str(run), 'Read the candidate check results',
         'Inspect the workflow for the repaired candidate, including its build, HTML and browser checks.'),
        (REPO + '/pull/40', 'Read the published release record',
         'The merged pull request records the Pages deployment and the 235 matching public targets.'),
    )
    items = ''.join('<li><a href="' + escape(url, quote=True) + '">' + label + '</a>. ' + description + '</li>'
                    for url, label, description in links)
    return (BEGIN + '\n<nav class="evidence-note" id="case-source-links" aria-labelledby="case-source-links-title">'
            '<h3 id="case-source-links-title">Open the original evidence</h3>'
            '<p>These public GitHub records document this site’s historical release.</p>'
            '<ol class="evidence-facts">' + items + '</ol></nav>\n' + END + '\n')


def decorate(page, body, root):
    if page['id'] != PAGE_ID:
        return body
    if BEGIN in body or 'id="case-source-links"' in body or body.count(ANCHOR) != 1:
        raise ValueError('Historical case sources require one unchanged evidence disclosure')
    return body.replace(ANCHOR, block(root) + ANCHOR, 1)
