from pathlib import Path
import json
from faster_whisper import WhisperModel
root=Path(__file__).resolve().parents[1]
source=root.parents[1]/'сценарии на 20.11'
paths=sorted(source.rglob('*.mp4'))
keys=['extra-long','extra-horror','mitsuri','makima','reze','stories','horror']
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=6)
for key,path in zip(keys,paths):
 dest=root/'sources/text'/f'video-{key}.json'
 if dest.exists(): continue
 segments,info=model.transcribe(str(path),language='ru',beam_size=5,vad_filter=True)
 rows=[]
 for s in segments:
  rows.append(dict(start=s.start,end=s.end,text=s.text))
  print(key,round(s.start,1),s.text,flush=True)
 dest.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
