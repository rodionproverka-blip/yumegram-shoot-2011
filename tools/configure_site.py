from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parents[1];d=ROOT/'dist'
p=d/'index.html';s=p.read_text().replace('07.11','20.11').replace('07 / 11','20 / 11').replace('Подключаем общие отметки…','Подключаем отметки смены…')
s=s.replace('<script src="migration-export.js" defer></script>','').replace('Исходный контент-план ↗','Материалы смены').replace('id="source-sheet" target="_blank" rel="noopener"','id="source-sheet"')
p.write_text(s)
p=d/'app.js';s=p.read_text().replace('07.11','20.11')
s=s.replace("const cover = {tifa:0, interview:0, tier:3, photo:1, spoiler:1, night:0}[video.id] ?? 0;", "const cover = video.cover ?? 0;")
s=s.replace("['tifa-01','01 / ПРЕДМЕТКА']", "['makima-08','Макима']").replace("['interview-01','02 / СКЕТЧ']", "['favorite-02','Диалоги']").replace("['tier-06','03 / ТИР-ЛИСТ']", "['reze-07','Резе']")
s=s.replace("const badge = visual.kind === 'source' ? visual.label + ' · ' + visual.time : 'Мультяшный черновик · ' + visual.label;", "const badge = visual.kind === 'source' ? visual.label + ' · ' + visual.time : visual.kind === 'photo' ? visual.label + ' · фото товара' : 'Схема кадра · ' + visual.label;")
s=s.replace("const watchLabel = video.category === 'edit' ? 'Готово' : 'Дубль проверен';", "const watchLabel = frame.role === 'Монтаж' || video.category === 'edit' ? 'Монтаж проверен' : 'Дубль проверен';")
s=s.replace("+ '<div id=\"video-content\">' + content", "+ (video.edits && tab === 'frames' ? '<section class=\"section edit-options\"><h2>Два монтажа из одной съёмки</h2><div class=\"prop-list\">' + video.edits.map(edit => '<article class=\"prop\"><h3>' + escape(edit.title) + '</h3><span class=\"muted\">' + escape(edit.duration) + '</span><p>' + escape(edit.text) + '</p></article>').join('') + '</div></section>' : '') + '<div id=\"video-content\">' + content")
s=s.replace("'<section class=\"section\"><div class=\"section-head\"><div><h2>Только монтаж</h2><p>Архив, графика и раскадровка для монтажёра.</p></div></div><div class=\"video-grid\">' + edit.map(videoCard).join('') + '</div></section></div>'", "(edit.length ? '<section class=\"section\"><h2>Только монтаж</h2><div class=\"video-grid\">' + edit.map(videoCard).join('') + '</div></section>' : '') + '</div>'")
s=s.replace("'К списку роликов ↓'", "'К списку роликов'")
s=s.replace("const printed = keys.filter(k => plan.props[k][2]);", "const printed = keys.filter(k => plan.props[k][2]);")
s=s.replace("  if (show('materials')) {", "  if (show('print') && !printed.length) sections.push('<p class=\"note\">Для этой смены печать не требуется. Тексты историй и экранные надписи готовим в телефоне и в монтаже.</p>');\n  if (show('materials')) {")
s=s.replace("Кнопки скачивают готовые файлы Word.", "Весь реквизит связан с роликами. Печатных материалов для этой смены нет.")
p.write_text(s)
