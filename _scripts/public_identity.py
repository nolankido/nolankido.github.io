"""Verified public-work profiles, separate from the richer identity document.

GitHub is the owner-approved account publishing this site's source. The DEV
profile identifies Nolan Kido and its Review Reply Writer article links to the
same GitHub account. These are identity links, not additional credentials.
"""
from html import escape


PROFILES = (
    ('https://github.com/nolankido', 'public code on GitHub'),
    ('https://dev.to/kidon', 'project writing on DEV'),
)


def same_as() -> list[str]:
    """Return a fresh list so one page cannot mutate another's identity."""
    return [url for url, _ in PROFILES]


def links() -> str:
    """The visible About links name the same profiles as its Person markup."""
    return ' and '.join(
        '<a href="' + escape(url, quote=True) + '" rel="me">' + escape(label) + '</a>'
        for url, label in PROFILES
    )
