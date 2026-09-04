"""Explicitly regenerate raw-byte integrity indexes after a reviewed export edit."""
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
SKIP={'.git','release-assets','work','node_modules','__pycache__'}
def main():
    entries=[]
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or any(x in SKIP for x in rel.parts) or rel.as_posix() in ['hashes/export-files.json','hashes/SHA256SUMS'] or p.name.endswith('.pyc'):continue
        raw=p.read_bytes();entries.append(dict(path=rel.as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    folder=ROOT/'hashes';folder.mkdir(exist_ok=True)
    (folder/'export-files.json').write_text(json.dumps(dict(schemaVersion=1,algorithm='sha256-raw-bytes',files=entries),indent=2)+'\n',encoding='utf-8',newline='\n')
    (folder/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in entries),encoding='utf-8',newline='\n')
    print(json.dumps(dict(files=len(entries),bytes=sum(x['bytes'] for x in entries),largestFileBytes=max(x['bytes'] for x in entries))))
if __name__=='__main__':main()
