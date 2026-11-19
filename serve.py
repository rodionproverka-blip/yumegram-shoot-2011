"""Run the private local shooting card and its persistent checklist API."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import argparse,json,sqlite3,re

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
DB=ROOT/'data/checklists.sqlite3'
DB.parent.mkdir(exist_ok=True)
with sqlite3.connect(DB) as connection:
 connection.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, operation TEXT UNIQUE NOT NULL, item TEXT NOT NULL, checked INTEGER NOT NULL CHECK (checked IN (0,1)))')

def allowed_keys():
 text=(DIST/'plan.js').read_text();plan=json.loads(text.split('=',1)[1].strip().rstrip(';'))
 keys={f'universal-{i}' for i in range(6)}|{f'prop-{key}' for key in plan['props']}|{f'prop-{p[0]}' for p in plan['shared']}
 for video in plan['videos']:
  key=video['id'];keys.update(f'{key}-check-{i}' for i in range(len(video['checks'])))
  for i,frame in enumerate(video['frames']):
   index=frame.get('checkIndex',i);keys.add(f'{key}-scene-{index}')
   if len(frame['visuals'])>1: keys.update(f'{key}-visual-{index}-{j}' for j in range(len(frame['visuals'])))
 return keys

def snapshot(connection):
 rows=connection.execute('SELECT item,checked FROM events e WHERE seq=(SELECT MAX(seq) FROM events WHERE item=e.item)').fetchall()
 revision=connection.execute('SELECT COALESCE(MAX(seq),0) FROM events').fetchone()[0]
 return {'revision':revision,'checked':[item for item,checked in rows if checked]}

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(DIST),**kwargs)
 def json(self,payload,status=200):
  data=json.dumps(payload,ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  if self.path.split('?')[0]=='/api/checklists':
   with sqlite3.connect(DB) as connection:self.json(snapshot(connection))
   return
  if self.path.startswith('/media/'):
   key=self.path.split('?')[0].removeprefix('/media/')
   manifest=json.loads((ROOT/'sources/videos.json').read_text())
   video=next((v for v in manifest if v['id']==key),None)
   if not video:self.send_error(404);return
   path=ROOT/video['file'];size=path.stat().st_size;start=0;end=size-1
   range_header=self.headers.get('Range')
   if range_header:
    match=re.fullmatch(r'bytes=(\d+)-(\d*)',range_header)
    if not match:self.send_error(416);return
    start=int(match[1]);end=min(int(match[2]) if match[2] else end,end)
    if start>end:self.send_error(416);return
   self.send_response(206 if range_header else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes')
   if range_header:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.send_header('Content-Length',str(end-start+1));self.end_headers()
   try:
    with path.open('rb') as f:
     f.seek(start);remaining=end-start+1
     while remaining:
      chunk=f.read(min(remaining,1024*1024))
      if not chunk:break
      self.wfile.write(chunk);remaining-=len(chunk)
   except (BrokenPipeError,ConnectionResetError):pass
   return
  return super().do_GET()
 def do_POST(self):
  if self.path!='/api/checklists':self.send_error(404);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size<=0 or size>32768:raise ValueError('size')
   data=json.loads(self.rfile.read(size));edits=data['edits'];keys=allowed_keys()
   if not isinstance(edits,list) or len(edits)>100:raise ValueError('edits')
   for edit in edits:
    if not isinstance(edit,dict) or edit.get('key') not in keys or type(edit.get('checked')) is not bool or not re.fullmatch(r'[\da-f]{8}(?:-[\da-f]{4}){3}-[\da-f]{12}',edit.get('id',''),re.I):raise ValueError('edit')
   with sqlite3.connect(DB,timeout=20) as connection:
    connection.execute('BEGIN IMMEDIATE')
    for edit in edits:
     existing=connection.execute('SELECT item,checked FROM events WHERE operation=?',(edit['id'],)).fetchone()
     if existing and existing!=(edit['key'],int(edit['checked'])):raise ValueError('operation already used')
     connection.execute('INSERT OR IGNORE INTO events(operation,item,checked) VALUES (?,?,?)',(edit['id'],edit['key'],int(edit['checked'])))
    self.json(snapshot(connection))
  except (ValueError,KeyError,TypeError):self.json({'error':'Invalid checklist operation'},400)
  except sqlite3.Error:self.json({'error':'Checklist temporarily unavailable'},503)
 def end_headers(self):
  if self.path.endswith(('.js','.html')):self.send_header('Cache-Control','no-cache')
  super().end_headers()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8780);parser.add_argument('--host',default='127.0.0.1');args=parser.parse_args()
 server=ThreadingHTTPServer((args.host,args.port),Handler)
 print(f'Съёмочная карта http://{args.host}:{args.port}/',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close()
