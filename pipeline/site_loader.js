// Loader for the hosted page (make_site.py puts this in site/index.html in place of the map's script).
// It fetches the data files named in data/manifest.json, unpacks the routes, puts the lines back in their order, and then starts the map's
// code (app.<hash>.js), which reads window.__DATA and window.__WATER exactly as the single-file page reads its inline data.
(async () => {
  const note = document.createElement('div');
  note.style.cssText = 'position:fixed;left:50%;top:45%;transform:translate(-50%,-50%);font:600 14px/1.4 system-ui,sans-serif;color:#555;background:rgba(255,255,255,.85);padding:10px 16px;border-radius:6px;z-index:99';
  note.textContent = 'Loading the timetables…'; document.body.appendChild(note);
  const unpack = r => {
    if (!r || !r.p) return r;
    const p = r.p, out = new Array(p.length / 3); let a = 0, b = 0, c = 0;
    for (let i = 0, j = 0; i < p.length; i += 3, j++) { a += p[i]; b += p[i + 1]; c += p[i + 2]; out[j] = [a / 1e6, b / 1e6, c / 10]; }
    return out;
  };
  try {
    const man = await (await fetch('data/manifest.json', { cache: 'no-cache' })).json();
    let done = 0;
    const got = await Promise.all(man.files.map(async f => {
      const r = await fetch('data/' + f.file); if (!r.ok) throw new Error(f.file + ': ' + r.status);
      const j = await r.json(); done++; note.textContent = `Loading the timetables… ${done} of ${man.files.length}`; return [f.name, j];
    }));
    const by = Object.fromEntries(got), core = by.core, water = by.water, lines = {};
    core.route = unpack(core.route); if (core.bl) core.bl.route = unpack(core.bl.route);
    for (const [name, j] of got) if (name !== 'core' && name !== 'water') for (const L of j.lines) { L.route = unpack(L.route); lines[L.key] = L; }
    core.lines = man.order.map(k => lines[k]).filter(Boolean);
    window.__DATA = core; window.__WATER = water;
    const s = document.createElement('script'); s.src = man.app;
    s.onload = () => note.remove(); s.onerror = () => { note.textContent = 'The map failed to load.'; };
    document.body.appendChild(s);
  } catch (e) { note.textContent = 'The map failed to load: ' + e.message; console.error(e); }
})();
