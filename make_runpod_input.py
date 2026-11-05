"""Create a RunPod request JSON locally. Does not submit requests or read credentials."""
import argparse,base64,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('portrait',type=Path);p.add_argument('--out',type=Path,default=Path('runpod-input.json'))
a=p.parse_args();suffix=a.portrait.suffix.lower()
if suffix not in ('.jpg','.jpeg','.png'):p.error('Use a JPG or PNG portrait.')
raw=a.portrait.read_bytes()
if len(raw)>5_000_000:p.error('Use a portrait under 5 MB to keep the JSON request manageable.')
if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')):p.error('File is not a PNG or JPEG.')
workflow=json.loads((Path(__file__).parent/'six-stickers-api.json').read_text())
name='portrait'+suffix;workflow['1']['inputs']['image']=name
request={'input':{'workflow':workflow,'images':[{'name':name,'image':base64.b64encode(raw).decode()}]}}
a.out.write_text(json.dumps(request))
print(f'Wrote {a.out}. This contains your portrait; keep it private. Nothing submitted.')
