"""Refresh byte counts and SHA-256 hashes for files already listed in PACKAGE_MANIFEST.json.

Run after editing a packaged file (for example LMOP_Explorer_Final.html):
  python scripts/update_manifest.py          # update changed entries
  python scripts/update_manifest.py --check  # report mismatches only, exit 1 if any
New files are never added and listed files are never removed; edit the manifest by hand for that.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 check='--check' in sys.argv[1:];path=ROOT/'PACKAGE_MANIFEST.json';manifest=json.loads(path.read_text(encoding='utf-8'));changed=[]
 for name,record in manifest['files'].items():
  p=(ROOT/name).resolve();assert p.is_relative_to(ROOT.resolve()) and p.is_file() and not p.is_symlink(),f'Missing or unsafe packaged file: {name}'
  current=dict(bytes=p.stat().st_size,sha256=sha(p))
  if current!={k:record.get(k) for k in current}:changed.append(name);record.update(current)
 for name in changed:print(('MISMATCH ' if check else 'updated ')+name)
 if check:sys.exit(1 if changed else 0)
 if changed:path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(f'{len(changed)} of {len(manifest["files"])} manifest entries {"updated" if changed else "already current"}.')
if __name__=='__main__':main()
