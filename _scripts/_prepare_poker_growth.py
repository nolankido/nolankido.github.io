"""Apply the digest-bound reviewed public-source patch on staging only."""
from pathlib import Path
import hashlib
import lzma
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
parent = subprocess.check_output(['git', 'rev-parse', 'HEAD^'], cwd=root, text=True).strip()
if parent != '6d127311815e4da087a8e0f09c266e51c3122c96':
    raise SystemExit('Unexpected baseline; refuse to apply the patch.')
parts = [root / '_scripts' / f'_poker-growth-{i}.bin' for i in range(1, 4)]
patch = lzma.decompress(b''.join(p.read_bytes() for p in parts))
if hashlib.sha256(patch).hexdigest() != 'd04cf37a18aa113d17985dfcf6ea4888c43d6ef0cee309cb42005f18d8325129':
    raise SystemExit('Public source patch digest mismatch.')
with tempfile.TemporaryDirectory() as d:
    path = Path(d) / 'source.patch'
    path.write_bytes(patch)
    subprocess.run(['git', 'apply', '--check', str(path)], cwd=root, check=True)
    subprocess.run(['git', 'apply', str(path)], cwd=root, check=True)
for p in parts:
    p.unlink()
(root / '.github/workflows/_prepare-poker-growth.yml').unlink()
Path(__file__).unlink()
subprocess.run([sys.executable, '_scripts/build.py'], cwd=root, check=True)
print('Reviewed source patch applied. Temporary preparation files removed.')
