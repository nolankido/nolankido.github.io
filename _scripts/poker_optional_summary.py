"""Extract visible titles of explicitly optional study disclosures, not answers."""
from html.parser import HTMLParser
import re


class OptionalStudySummaries(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}
    EXCLUDED = {'script', 'style', 'nav', 'noscript', 'template'}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.sections = []
        self.blocked = []
        self.stack = []
        self.anchor = None
        self.summary = None
        self.reading_summary = False
        self.feed(source)
        self.close()
        if self.stack:
            raise ValueError('Unclosed optional study disclosure')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.stack:
            if self.reading_summary:
                raise ValueError('Optional study summary must be plain visible text')
            if len(self.stack) == 1 and tag == 'summary':
                if self.summary is not None or 'hidden' in attrs or attrs.get('aria-hidden') == 'true':
                    raise ValueError('Optional study disclosure needs one visible summary')
                self.summary = []
                self.reading_summary = True
            if tag not in self.VOID:
                self.stack.append(tag)
            return
        if self.blocked:
            if tag not in self.VOID:
                self.blocked.append(tag)
            return
        hidden = 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        if tag in self.EXCLUDED or hidden or tag == 'details':
            if tag == 'details' and not hidden and attrs.get('data-reading-optional') == 'true':
                anchor = attrs.get('id', '')
                if not re.fullmatch(r'[a-z][a-z0-9-]*', anchor):
                    raise ValueError('Optional study disclosure needs a safe anchor')
                if any(row['anchor'] == anchor for row in self.sections):
                    raise ValueError('Duplicate optional study anchor: ' + anchor)
                self.anchor = anchor
                self.stack.append(tag)
            elif tag not in self.VOID:
                self.blocked.append(tag)

    def handle_startendtag(self, tag, attrs):
        if self.reading_summary:
            raise ValueError('Optional study summary must be plain visible text')
        if self.stack and tag not in self.VOID:
            raise ValueError('Optional study disclosure contains self-closing nonvoid markup')
        if not self.blocked and tag == 'details' and dict(attrs).get('data-reading-optional') == 'true':
            raise ValueError('Optional study disclosure cannot be self-closing')

    def handle_data(self, data):
        if self.reading_summary:
            self.summary.append(data)

    def handle_endtag(self, tag):
        if self.stack:
            if not self.stack or self.stack[-1] != tag:
                raise ValueError('Unbalanced markup in optional study disclosure')
            if self.reading_summary:
                self.reading_summary = False
            self.stack.pop()
            if not self.stack:
                title = ' '.join(''.join(self.summary or []).split())
                if not title:
                    raise ValueError('Optional study disclosure needs a nonempty summary')
                self.sections.append({'anchor': self.anchor, 'title': title, 'text': title})
                self.anchor = self.summary = None
        elif self.blocked:
            # Match the closing tag instead of allowing an unrelated close to
            # release a hidden ancestor. Unclosed excluded blocks stay excluded.
            if tag == self.blocked[-1]:
                self.blocked.pop()


def optional_summary_sections(source):
    """Return summary-only search passages in document order."""
    if 'data-reading-optional' not in source:
        return []
    return OptionalStudySummaries(source).sections
