"""Remove only the reviewed evidence navigation from its one historical page."""
from hashlib import sha256
import re

PATH = 'technology/checking-ai-website-changes/index.html'
# Frozen after review. No source module or mutable test output supplies this value.
BLOCK_SHA256 = 'a7b51fc5af8c5056a1bc44130f314621de4c5e1d70ce9de38455439b0d7b1a3f'


def before(path, data):
    if str(path) != PATH:
        return data
    binary = isinstance(data, bytes)
    text = data.decode() if binary else data
    match = re.search(r'<!-- Historical case sources: start -->.*?<!-- Historical case sources: end -->\n', text, re.S)
    if match and sha256(match[0].encode()).hexdigest() == BLOCK_SHA256:
        text = text.replace(match[0], '', 1)
    return text.encode() if binary else text
