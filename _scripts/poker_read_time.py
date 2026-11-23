"""Reader time for core article text, excluding explicitly optional extensions."""
from html.parser import HTMLParser
from math import ceil
import re


class PlainText(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored = 0
        self.optional_details = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == 'details' and (self.optional_details or dict(attrs).get('data-reading-optional') == 'true'):
            self.optional_details += 1
        if tag in ('script', 'style'):
            self.ignored += 1

    def handle_endtag(self, tag):
        if tag == 'details' and self.optional_details:
            self.optional_details -= 1
        if tag in ('script', 'style'):
            self.ignored = max(0, self.ignored - 1)

    def handle_data(self, value):
        if not self.ignored and not self.optional_details:
            self.parts.append(value)


def minutes(source):
    """225 words/minute, including ordinary answers, excluding labelled optional study."""
    clean = re.sub(r'\$\{[a-z_]+\}', '', ' '.join(PlainText(source).parts))
    return max(1, ceil(len(clean.split()) / 225))
