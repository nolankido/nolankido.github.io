"""Apply a digest-bound public-source patch to the reviewed baseline."""
from pathlib import Path
import hashlib
import lzma
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
def run(*args):
    return subprocess.check_output(list(args), cwd=root, text=True).strip()
if run('git', 'rev-parse', 'HEAD^') != '600c51b13bb95b7e5389203e61e6c7624d972b83':
    raise SystemExit('Unexpected baseline; patch not applied.')
parts = [root / '_scripts' / f'_viewer-next-{i}.bin' for i in range(1, 4)]
patch = lzma.decompress(b''.join(p.read_bytes() for p in parts))
if hashlib.sha256(patch).hexdigest() != '0b977b2287c0fe48dda66961140380991047d1be408263724b1bcb86109fcfda':
    raise SystemExit('Public source patch digest mismatch.')
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'public-source.patch'
    path.write_bytes(patch)
    subprocess.run(['git', 'apply', '--check', str(path)], cwd=root, check=True)
    subprocess.run(['git', 'apply', str(path)], cwd=root, check=True)
for p in parts:
    p.unlink()
(root / '.github/workflows/_prepare-viewer-next.yml').unlink()
Path(__file__).unlink()
subprocess.run([sys.executable, '_scripts/build.py'], cwd=root, check=True)
run('git', 'add', '-A')
tree = run('git', 'write-tree')
if tree != '4b0eed03c6607dbca21f13cd02672ab18125ffc9':
    raise SystemExit(f'Prepared tree differs from local reviewed source: {tree}')
print('PREPARED_TREE=' + tree)
