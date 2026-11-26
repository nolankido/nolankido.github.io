"""Build a minimal test-only search sitemap with the mandatory Playbook.

Never relax the production audit to make a partial test fixture pass.
"""
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET

import tenbb_companion


def complete_audit_fixture(root: Path, source_root: Path, canonical_urls) -> None:
    """Copy the approved companion and add its real canonical and revision."""
    urls = list(canonical_urls)
    approved = tenbb_companion.record(source_root)
    if len(urls) != len(set(urls)) or approved['url'] in urls:
        raise ValueError('Duplicate canonical in minimal search audit fixture')
    if root.resolve() == source_root.resolve():
        raise ValueError('Search audit fixture must not overwrite its source')
    for relative in (tenbb_companion.OUTPUT, tenbb_companion.CODE, tenbb_companion.WORKSHEET):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / relative, target)
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in urls:
        ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = url
    tenbb_companion.add_to_sitemap(sitemap, root)
    (root / 'sitemap.xml').write_bytes(ET.tostring(sitemap, encoding='utf-8'))
