"""Keep standalone book discovery metadata tied to visible, reviewed content."""
from html.parser import HTMLParser
from search_metadata_contract import inspect_metadata


class Metadata(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.values = {'title': [], 'h1': []}
        self.capture = None
        self.parts = []
        self.canonicals = []
        self.meta = []
        self.feed(document)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in self.values:
            self.capture = tag
            self.parts = []
        elif tag == 'link':
            if 'canonical' in (attributes.get('rel') or '').lower().split():
                self.canonicals.append(attributes.get('href'))
        elif tag == 'meta':
            self.meta.append(attributes)

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            self.values[tag].append(' '.join(''.join(self.parts).split()))
            self.capture = None


def validate(document, *, title, heading, description, url, schema):
    """Reject missing, duplicated or conflicting search and sharing signals.

    The caller separately checks exact source/output equality and Book
    provenance. This parser checks the actual visible title and metadata,
    including escaped text and differently ordered HTML attributes.
    """
    doc = Metadata(document)
    if doc.values['title'] != [title] or doc.values['h1'] != [heading]:
        raise ValueError('Book title or visible heading differs from reviewed metadata: ' + url)
    if doc.canonicals != [url]:
        raise ValueError('Book must have one exact canonical: ' + url)
    expected = {'description': description, 'og:title': title,
                'og:description': description, 'og:url': url,
                'twitter:title': title, 'twitter:description': description}
    values, _, errors = inspect_metadata(doc.meta, expected_noindex=False)
    blocking = [error for error in errors if 'crawl policy' in error]
    if blocking:
        raise ValueError('Book must remain indexable: ' + url + ': ' + '; '.join(blocking))
    if errors:
        raise ValueError('Book search/share metadata mismatch: ' + url + ': ' + '; '.join(errors))
    for name, value in expected.items():
        if values.get(name) != value:
            raise ValueError('Book search/share metadata mismatch (' + name + '): ' + url)
    if (not isinstance(schema, dict)
            or schema.get('name') != title
            or schema.get('description') != description
            or schema.get('url') != url
            or not isinstance(schema.get('mainEntity'), dict)
            or schema['mainEntity'].get('name') != heading):
        raise ValueError('Book structured identity differs from reviewed metadata: ' + url)


def validate_page_identity(schema, *, url, origin, author_id):
    """Resolve the reviewed page and publisher identities, not just their references."""
    if not isinstance(schema, dict) or schema.get('@id') != url + '#webpage':
        raise ValueError('Book page must define its canonical WebPage identity: ' + url)
    website = schema.get('isPartOf')
    if (not isinstance(website, dict)
            or website.get('@type') != 'WebSite'
            or website.get('@id') != origin + '/#website'
            or website.get('url') != origin + '/'):
        raise ValueError('Book page must belong to the canonical WebSite: ' + url)
    publisher = website.get('publisher')
    if (not isinstance(publisher, dict)
            or publisher.get('@type') != 'Person'
            or publisher.get('@id') != author_id
            or publisher.get('url') != author_id.split('#', 1)[0]):
        raise ValueError('Book page must identify the reviewed Person publisher: ' + url)
