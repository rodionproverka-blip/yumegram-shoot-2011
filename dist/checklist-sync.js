'use strict';

window.createChecklistSync = function createChecklistSync(keys, onUpdate) {
  const cacheKey = 'yumegram-shoot-2011-shared-v1';
  const opPrefix = cacheKey + '-op-';
  let snapshot = read(cacheKey, {revision: 0, checked: []});
  let running = false;
  let status = 'connecting';

  function read(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
    catch { return fallback; }
  }
  function pending() {
    const operations = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith(opPrefix)) {
        const operation = read(key, null);
        if (operation && keys.has(operation.key)) operations.push(operation);
      }
    }
    return operations.sort((a, b) => a.at - b.at || a.id.localeCompare(b.id));
  }
  function current() {
    const checked = new Set(snapshot.checked.filter(key => keys.has(key)));
    for (const operation of pending()) {
      if (operation.checked) checked.add(operation.key);
      else checked.delete(operation.key);
    }
    return checked;
  }
  function notify() { onUpdate(current(), status, pending().length); }
  async function sync() {
    if (running) return;
    running = true;
    const edits = pending().slice(0, 100);
    try {
      const response = await fetch(location.hostname === '127.0.0.1' ? '/api/checklists' : 'https://yumegram-shoot-0711-checklists.rodionproverka393682.chatgpt.site/api/checklists', edits.length ? {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({legacy: [], edits: edits.map(edit => ({...edit, key: "2011-" + edit.key}))}),
      } : {cache: 'no-store'});
      if (!response.ok) throw new Error('Checklist unavailable');
      const next = await response.json();
      if (next.revision >= snapshot.revision) {
        snapshot = {...next, checked: location.hostname === "127.0.0.1" ? next.checked : next.checked.filter(key => key.startsWith("2011-")).map(key => key.slice(5))};
        localStorage.setItem(cacheKey, JSON.stringify(snapshot));
      }
      for (const edit of edits) localStorage.removeItem(opPrefix + edit.id);
      status = 'synced';
    } catch { status = 'offline'; }
    running = false;
    notify();
  }
  return {
    current,
    set(key, checked) {
      if (!keys.has(key)) return;
      const operation = {id: crypto.randomUUID(), key, checked, at: Date.now()};
      localStorage.setItem(opPrefix + operation.id, JSON.stringify(operation));
      notify();
      sync();
    },
    start() {
      sync();
      setInterval(sync, 5000);
      window.addEventListener('focus', sync);
      window.addEventListener('online', sync);
      window.addEventListener('storage', event => {
        if (event.key === cacheKey) snapshot = read(cacheKey, snapshot);
        notify();
      });
    },
  };
};
