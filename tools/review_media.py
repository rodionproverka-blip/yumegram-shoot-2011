from pathlib import Path
import subprocess,json,math,hashlib
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parents[1]/"сценарии на 20.11"
OUT=ROOT/"sources/analysis"
records=[]
for idx,video in enumerate(sorted(SOURCE.rglob("*.mp4"))):
 info=json.loads(subprocess.check_output(["ffprobe","-v","quiet","-show_format","-of","json",str(video)]))
 dur=float(info["format"]["duration"])
 key=["extra-long","extra-horror","mitsuri","makima","reze","stories","horror"][idx]
 frames=[]
 times=[round(i*(dur-0.3)/23,2) for i in range(24)]
 for i,t in enumerate(times):
  dest=OUT/f"{key}-{i:02d}.png"
  subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i",str(video),"-frames:v","1","-vf","scale=200:-2",str(dest)],check=True)
  frames.append(dest)
 sheet=Image.new("RGB",(6*200,4*384),"#222")
 draw=ImageDraw.Draw(sheet)
 for i,dest in enumerate(frames):
  im=Image.open(dest); im.thumbnail((196,352));x=(i%6)*200;y=(i//6)*384
  sheet.paste(im,(x,y));draw.text((x+5,y+355),f"{key} {times[i]:.1f}s",fill="white")
 sheet.save(OUT/f"{key}-sheet.jpg")
 records.append(dict(id=key,file=str(video),duration=dur,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),sampleTimes=times))
(ROOT/"sources/videos.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
for folder in sorted((SOURCE/"фигурки").iterdir()):
 photos=sorted(folder.glob("*.jpg"))
 if not photos: continue
 sheet=Image.new("RGB",(1200,math.ceil(len(photos)/4)*440),"#222")
 draw=ImageDraw.Draw(sheet)
 for i,photo in enumerate(photos):
  im=ImageOps.exif_transpose(Image.open(photo));im.thumbnail((294,402));x=i%4*300;y=i//4*440
  sheet.paste(im,(x,y));draw.text((x+5,y+412),f"photo {i+1}",fill="white")
 key="mitsuri" if "Mitsuri" in folder.name else "makima" if "Makima" in folder.name else "reze"
 sheet.save(OUT/f"{key}-photos.jpg")
 print(key, [p.name for p in photos],flush=True)
