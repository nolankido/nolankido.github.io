"""Render an explicitly editorial decision guide. No scoring, AI, or network."""
from html import escape
from pathlib import Path
import json
import re

SHEET = Path('downloads/should-i-use-ai.txt')

def questions(root: Path) -> str:
    data = json.loads((root / '_source/ai-task-choice.json').read_text(encoding='utf-8'))
    expected = {'goal': {'clear', 'unclear'}, 'inputs': {'allowed', 'restricted', 'unknown'},
                'stakes': {'low', 'high'}, 'review': {'ready', 'missing'},
                'simpler': {'yes', 'no', 'unknown'}, 'scope': {'draft', 'action'}}
    if not isinstance(data, list) or [q.get('id') for q in data] != list(expected):
        raise ValueError('The six questions must retain their named order')
    parts = []
    for number, q in enumerate(data, 1):
        key = q['id']
        options = q.get('options')
        if (not isinstance(options, list) or any(not isinstance(o, list) or len(o) != 2 for o in options)
            or len(options) != len(expected[key]) or {o[0] for o in options} != expected[key]):
            raise ValueError('Question options must match the decision rules')
        if any(not isinstance(t, str) or not t.strip() for t in [q.get('title'), q.get('help'), *[o[1] for o in options]]):
            raise ValueError('Every question and option needs descriptive text')
        controls = ''.join('<label for="choice-' + key + '-' + value + '"><input type="radio" name="' + key
            + '" id="choice-' + key + '-' + value + '" value="' + value + '" required> <span>'
            + escape(label) + '</span></label>' for value, label in options)
        parts.append('<fieldset aria-describedby="choice-' + key + '-help"><legend>' + str(number) + '. '
            + escape(q['title']) + '</legend><p class="choice-help" id="choice-' + key + '-help">'
            + escape(q['help']) + '</p>' + controls + '</fieldset>')
    return ''.join(parts)
