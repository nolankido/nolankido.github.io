"""Check the site's canonical sitemap structure without making network requests."""
from datetime import date
from pathlib import Path
import re
from xml.etree import ElementTree as ET

NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def inspect_sitemap(path: Path):
    """Return the parsed tree, direct canonical locations, and structural errors.

    The site's generator emits URL records with one loc and an optional
    calendar-date lastmod. Inventory equality and reviewed book dates are
    checked separately by the existing search audit.
    """
    try:
        tree = ET.parse(path).getroot()
    except (OSError, ET.ParseError, ValueError) as exc:
        return ET.Element(NS + 'urlset'), [], ['Cannot read sitemap XML: ' + str(exc)]
    errors = []
    locations = []
    if tree.tag != NS + 'urlset':
        errors.append('Sitemap must use the standard urlset namespace')
    for index, entry in enumerate(tree, 1):
        label = 'Sitemap record ' + str(index)
        if entry.tag != NS + 'url':
            errors.append(label + ' must be a direct url element')
            continue
        locs = entry.findall(NS + 'loc')
        if len(locs) != 1 or len(locs[0]) or not locs[0].text or locs[0].text != locs[0].text.strip():
            errors.append(label + ' must contain exactly one nonempty direct loc')
        else:
            locations.append(locs[0].text)
        dates = entry.findall(NS + 'lastmod')
        if len(dates) > 1:
            errors.append(label + ' contains duplicate lastmod elements')
        elif dates:
            value = dates[0].text or ''
            try:
                if len(dates[0]) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError('expected a calendar date')
                date.fromisoformat(value)
            except ValueError:
                errors.append(label + ' has an invalid lastmod calendar date')
        if any(child.tag not in {NS + 'loc', NS + 'lastmod'} for child in entry):
            errors.append(label + ' contains an unexpected sitemap field')
    if not locations:
        errors.append('Sitemap has no valid direct canonical locations')
    return tree, locations, errors
