"""Read-only node/model compatibility check against a running ComfyUI URL."""
import argparse,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('url',help='ComfyUI root URL, e.g. http://127.0.0.1:8188');a=p.parse_args()
with urllib.request.urlopen(a.url.rstrip('/')+'/object_info',timeout=30) as r:info=json.load(r)
graph=json.loads((Path(__file__).parent/'six-stickers-api.json').read_text());errors=set()
for key,node in graph.items():
 kind=node['class_type']
 if kind not in info:errors.add('Missing node: '+kind);continue
 schema=info[kind]['input'];fields={**schema.get('required',{}),**schema.get('optional',{})}
 for name in schema.get('required',{}):
  if name not in node['inputs']:errors.add(f'{kind}: missing required input {name}')
 for name,value in node['inputs'].items():
  if name not in fields:errors.add(f'{kind}: unsupported input {name}');continue
  expected=fields[name][0]
  if isinstance(value,list):
   source,slot=value;source_kind=graph[source]['class_type']
   if source_kind in info:
    outputs=info[source_kind]['output']
    if slot>=len(outputs):errors.add(f'{kind}.{name}: invalid source slot {slot}')
    elif isinstance(expected,str) and expected!='*' and outputs[slot]!=expected:errors.add(f'{kind}.{name}: {outputs[slot]} does not match {expected}')
  elif isinstance(expected,list) and value not in expected:
   # Uploaded file does not have to exist until test input is supplied.
   if not (kind=='LoadImage' and name=='image'):errors.add(f'{kind}.{name}: unavailable option/model {value!r}')
if errors:
 print('\n'.join(sorted(errors)));raise SystemExit(1)
print('PASS: required nodes, model selections and linked socket types match this server. No GPU job submitted.')
