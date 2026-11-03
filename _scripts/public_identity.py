"""Verified public-work profiles, separate from the richer identity document.

GitHub is the owner-approved account publishing this site's source. The DEV profile identifies Nolan Kido and links to the same GitHub account.
The public Substack identifies Nolan Kido and links back to this site; the
NolanPoker channel says it is Nolan Kido's tournament vlog and is linked from
his public video pages. These are identity links, not credentials.
"""
from html import escape


PROFILES = (
    ('https://github.com/nolankido', 'public code on GitHub'),
    ('https://dev.to/kidon', 'project writing on DEV'),
    ('https://nolankido.substack.com/', 'long-form AI writing on Substack'),
    ('https://www.youtube.com/@NolanPoker', 'NolanPoker tournament videos on YouTube'),
)


def same_as() -> list[str]:
    """Return a fresh list so one page cannot mutate another's identity."""
    return [url for url, _ in PROFILES]


def links() -> str:
    """The visible About links name the same profiles as its Person markup."""
    anchors = [
        '<a href="' + escape(url, quote=True) + '" rel="me">' + escape(label) + '</a>'
        for url, label in PROFILES
    ]
    if len(anchors) < 3:
        return ' and '.join(anchors)
    return ', '.join(anchors[:-1]) + ', and ' + anchors[-1]
