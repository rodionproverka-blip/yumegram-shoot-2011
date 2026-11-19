from pathlib import Path
import json,shutil,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT/'sources/videos.json'
records=json.loads(VIDEO.read_text())
(ROOT/'sources/videos').mkdir(exist_ok=True)
for v in records:
 src=Path(v['file'])
 if not src.is_absolute():src=ROOT/src
 dest=ROOT/'sources/videos'/f"{v['id']}.mp4"
 if not dest.exists():shutil.copy2(src,dest)
 v['originalFile']=v.get('originalFile',str(src));v['file']=str(dest.relative_to(ROOT))
VIDEO.write_text(json.dumps(records,ensure_ascii=False,indent=2))
assets=ROOT/'dist/assets/scripts';assets.mkdir(exist_ok=True)
for i,doc in enumerate(json.loads((ROOT/'sources/documents.json').read_text())):
 dest=assets/f'original-{i+1:02d}.docx'
 shutil.copy2(doc['source'],dest)
 doc['download']=str(dest.relative_to(ROOT/'dist'))
 (assets/f'original-{i+1:02d}.txt').write_text((ROOT/doc['text']).read_text())
recordsDocs=json.loads((ROOT/'sources/documents.json').read_text())
names={'mitsuri':'Мицури — комментарии Паши','makima':'Макима — комментарии Паши','reze':'Резе — комментарии Паши','stories':'Истории коллекционеров — пример подачи','horror':'Что может пойти не так — монтажные вставки','extra-long':'Дополнительный пример подачи','extra-horror':'Дополнительная копия монтажного примера'}
parts=['<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Материалы смены 20.11</title><link rel="stylesheet" href="style.css"><main class="shell"><div class="page-head"><a class="btn" href="index.html">Съёмочная карта</a><h1>Материалы смены 20.11</h1><p>Видео с комментариями, примеры подачи и исходные сценарии.</p></div>']
for v in records:
 transcript=json.loads((ROOT/'sources/text'/f"video-{v['id']}.json").read_text())
 paragraphs=''.join(f'<p><small class="mono">{int(row["start"])//60}:{int(row["start"])%60:02d}</small> {html.escape(row["text"])}</p>' for row in transcript)
 parts.append(f'<section class="section panel"><h2>{names[v["id"]]}</h2><video controls preload="none" style="width:min(100%,480px);max-height:600px" src="/media/{v["id"]}"></video><details><summary>Расшифровка комментариев</summary>{paragraphs}</details></section>')
parts.append('<section class="section"><h2>Исходные документы</h2><div class="prop-list">')
for i,doc in enumerate(recordsDocs):
 parts.append(f'<article class="prop"><h3>{html.escape(Path(doc["source"]).stem)}</h3><a class="btn small" href="assets/scripts/original-{i+1:02d}.docx" download>Скачать исходный сценарий</a></article>')
parts.append('</div></section><section class="section"><h2>Уточнения съёмочной версии</h2><p>У Мицури добавлена карточка выпуска с закрытым индивидуальным номером. У Резе уточнены низкие ракурсы, блеск покраски и коврик. Макима подготовлена одним сценарием для двух монтажей.</p><p>В документе историй восемь текстов. Каждый сохранён отдельным дублем. Хронометраж рассчитан по объёму чтения. Для «Дюны» отведено около 47 секунд, в начале «за полминуты» заменено на «коротко».</p><p>Факты о третьей «Дюне» сверены по <a href="https://www.dunemovie.com/home/" target="_blank" rel="noopener">официальному сайту фильма</a> и <a href="https://www.cma.gov.ae/news/abu-dhabis-liwa-desert-opens-the-first-look-teaser-trailer-of-hotly-anticipated-dune%3A-part-three" target="_blank" rel="noopener">анонсу Creative Media Authority</a>.</p><p>Для отсутствующих кадров распаковки использованы схемы. Геометрию ячеек и реальные крепления сверяем с упаковкой перед дублем. Иллюстрации развлекательных роликов задают композицию, конкретные фигурки выбираем из вашей витрины.</p></section></main></html>')
(ROOT/'dist/sources.html').write_text(''.join(parts))
