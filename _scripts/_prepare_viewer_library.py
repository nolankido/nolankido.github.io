"""Apply the digest-bound public educational source patch on staging only."""
from pathlib import Path
import hashlib
import lzma
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
parent = subprocess.check_output(['git', 'rev-parse', 'HEAD^'], cwd=root, text=True).strip()
if parent != '0cd27e76fbcba5f1d15b573fe62bf930693b9ba8':
    raise SystemExit('Unexpected baseline. Review current main before applying.')
parts = [root / '_scripts' / f'_viewer-library-{i}.bin' for i in range(1, 4)]
patch = lzma.decompress(b''.join(path.read_bytes() for path in parts))
if hashlib.sha256(patch).hexdigest() != 'bbf5617c2d8e201c55b1e29c5f12fffb5b81455bc345a40f61468cd0c74cc595':
    raise SystemExit('Source patch digest mismatch.')
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'source.patch'
    path.write_bytes(patch)
    subprocess.run(['git', 'apply', '--check', str(path)], cwd=root, check=True)
    subprocess.run(['git', 'apply', str(path)], cwd=root, check=True)
for path in parts:
    path.unlink()
(root / '.github/workflows/_prepare-viewer-library.yml').unlink()
Path(__file__).unlink()
subprocess.run([sys.executable, '_scripts/build.py'], cwd=root, check=True)
subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
tree = subprocess.check_output(['git', 'write-tree'], cwd=root, text=True).strip()
if tree != 'cd9e1ca03d61081937daa5a4c097f3459b74ed6f':
    raise SystemExit('Prepared tree differs from locally reviewed tree: ' + tree)
print('PREPARED_TREE=' + tree, flush=True)
