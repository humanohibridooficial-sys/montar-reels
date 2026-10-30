# CSS y JS comunes de las piezas (venían de herramientas/reel-mister/build.py). montar.py los inserta en index.html.
CSS = '''
  #talkwrap { position: absolute; inset: 0; transform-origin: 50% 42%; }
  .tile { position: absolute; inset: 0; opacity: 0; overflow: hidden; }
  .tile video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  .tile.card { inset: auto; left: 280px; top: 470px; width: 520px; height: 760px; border-radius: 30px; box-shadow: 0 26px 60px #0005; z-index: 3; }
  #subs { position: absolute; left: 7%; right: 7%; top: 1040px; height: 260px; pointer-events: none; }
  #subs .sb { position: absolute; left: 0; right: 0; top: 0; display: flex; flex-direction: column; align-items: center; opacity: 0;
    text-align: center; text-shadow: 0 3px 14px #000b, 0 0 2px #0008; }
  #subs .l1 { font: 800 54px/1.15 Inter, sans-serif; color: #fff; }
  #subs .l2 { font: 900 96px/1.02 Inter, sans-serif; color: #E0B83C; letter-spacing: -.01em; -webkit-text-stroke: 2px #070D16; paint-order: stroke fill; }
  #subs .l2.s { font: italic 600 112px/1.0 Playfair, serif; letter-spacing: 0; }
  #panel { position: absolute; inset: 0; opacity: 0; z-index: 2; background: linear-gradient(180deg, #F6F9FC 0%, #EEF2F6 55%, #8C96A3 100%); }
  #panel .hd { position: absolute; left: 0; right: 0; top: 250px; text-align: center; opacity: 0; }
  #panel .h1 { font: 800 56px/1.1 Inter, sans-serif; color: #2E6BFF; }
  #panel .h2 { font: italic 600 88px/1.05 Playfair, serif; color: #8A6508; margin-top: 18px; }
  #panel .bl { position: absolute; left: 250px; top: 1275px; display: flex; flex-direction: column; gap: 16px; }
  #panel .b { display: flex; align-items: center; gap: 22px; font: 800 48px/1 Inter, sans-serif; color: #070D16; opacity: 0; }
  #panel .b i { width: 28px; height: 28px; border-radius: 50%; background: #E0B83C; box-shadow: 0 0 0 5px #E0B83C40; }
  #num { position: absolute; left: 0; right: 0; top: 900px; text-align: center; opacity: 0; font: 900 380px/1 Inter, sans-serif; color: #fff;
    text-shadow: 0 10px 40px #000a; }
  #tachado { position: absolute; left: 0; right: 0; top: 1060px; display: flex; justify-content: center; opacity: 0; }
  #tachado span { position: relative; font: 900 92px/1 Inter, sans-serif; color: #fff; text-shadow: 0 4px 18px #000b; }
  #tachado b { position: absolute; left: -4%; right: -4%; top: 46%; height: 14px; border-radius: 7px; background: #E5322D; transform: scaleX(0); transform-origin: 0 50%; }
  #leak { position: absolute; inset: -10%; opacity: 0; z-index: 9; pointer-events: none; mix-blend-mode: screen; filter: blur(30px);
    background: radial-gradient(circle at 30% 38%, #fffbe6 0%, #ffe08a 30%, #ffc94400 62%), radial-gradient(circle at 78% 72%, #ffffff 0%, #fff0b8 28%, #ffffff00 60%), #fff3c4; }
  #follow { position: absolute; left: 50%; top: 250px; width: 700px; margin-left: -350px; opacity: 0; z-index: 8; display: flex; align-items: center; gap: 24px;
    background: #fff; border-radius: 30px; padding: 24px 28px; box-shadow: 0 20px 50px #0006; box-sizing: border-box; }
  #follow .av { width: 96px; height: 96px; border-radius: 50%; background: #070D16; display: grid; place-items: center; font: 400 40px/1 Anton, sans-serif; color: #E0B83C; flex: none; }
  #follow .nm { font: 800 40px/1.1 Inter, sans-serif; color: #111; }
  #follow .hn { font: 500 30px/1.2 Inter, sans-serif; color: #8A8F98; }
  #follow .bt { position: absolute; right: 28px; top: 50%; margin-top: -36px; height: 72px; padding: 0 34px; border-radius: 18px; display: grid; place-items: center;
    font: 800 34px/1 Inter, sans-serif; }
  #follow .b1 { background: #2E6BFF; color: #fff; }
  #follow .b2 { background: #EFEFEF; color: #111; opacity: 0; }
  .tile.split { inset: auto; left: 0; top: 0; width: 1080px; height: 820px; -webkit-mask-image: linear-gradient(#000 82%, #0000); }
  #tops { position: absolute; left: 6%; right: 6%; top: 210px; pointer-events: none; z-index: 7; }
  #tops .tp { position: absolute; left: 0; right: 0; top: 0; text-align: center; opacity: 0; text-shadow: 0 4px 18px #000c, 0 0 3px #0009; }
  #tops .t1 { font: 800 62px/1.1 Inter, sans-serif; color: #fff; }
  #tops .t2 { font: 900 112px/1 Inter, sans-serif; color: #E0B83C; text-transform: uppercase; -webkit-text-stroke: 2px #070D16; paint-order: stroke fill; }
  #tops .t2.s { font: italic 600 124px/1 Playfair, serif; text-transform: none; margin-top: 16px; }
'''

JS = '''
  // ---- montaje estilo Carla: reencuadres, BYN, b-roll, panel, cifra, tachado, destellos, subtítulos, perfil ----
  const PLAN = __PLAN__;
  const $id = (x) => document.getElementById(x);
  const tw = $id('talkwrap');
  PLAN.zoom.forEach(([t, z]) => tl.set(tw, { scale: z }, t));
  tl.set(tw, { filter: 'grayscale(1) contrast(1.1)' }, PLAN.byn[0]).set(tw, { filter: 'none' }, PLAN.byn[1]);
  PLAN.spans.forEach(([k, t0, t1, c]) => {
    const el = $id('t-' + k);
    tl.addLabel('scene:broll-' + k, t0);
    if (c === 'split') {   // b-roll arriba; el plano a cámara y los subtítulos bajan
      tl.set(el, { opacity: 1 }, t0).fromTo(el, { y: -60 }, { y: 0, duration: 0.3, ease: 'power3.out', immediateRender: false }, t0);
      tl.set(tw, { y: 340 }, t0).set(tw, { y: 0 }, t1).set('#subs', { y: 330 }, t0).set('#subs', { y: 0 }, t1);
    } else if (c === 'card') tl.set(el, { opacity: 1 }, t0).fromTo(el, { scale: 0.94 }, { scale: 1, duration: 0.3, ease: 'back.out(1.6)', immediateRender: false }, t0);
    else tl.set(el, { opacity: 1 }, t0).fromTo(el, { scale: 1.0 }, { scale: 1.07, duration: t1 - t0, ease: 'none', immediateRender: false }, t0);
    tl.set(el, { opacity: 0 }, t1);
  });
  // Titular de arriba por idea; el del gancho ya está en el fotograma 0.
  const tops = $id('tops');
  PLAN.tops.forEach(([t0, t1, a, b, serif]) => {
    const el = document.createElement('div');
    el.className = 'tp';
    el.innerHTML = `<div class="t1">${esc(a)}</div><div class="t2${serif ? ' s' : ''}">${esc(b)}</div>`;
    tops.appendChild(el);
    if (t0 === 0) el.style.opacity = 1;   // un set en 0 no pinta el fotograma 0: se deja visible de base
    else tl.fromTo(el, { opacity: 0, y: -24 }, { opacity: 1, y: 0, duration: 0.22, ease: 'back.out(1.8)', immediateRender: false }, t0);
    tl.set(el, { opacity: 0 }, t1);
  });
  // Pantalla clara: cabecera que cambia con cada punto y lista que se va completando.
  const [p0, p1, p2, p3] = PLAN.panel, pn = $id('panel');
  tl.set(pn, { opacity: 1 }, p0).set(pn, { opacity: 0 }, p3);
  const hds = pn.querySelectorAll('.hd'), bls = pn.querySelectorAll('.b');
  [p0, p1, p2].forEach((t, i) => {
    tl.fromTo(hds[i], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.25, ease: 'power2.out', immediateRender: false }, t);
    if (i < 2) tl.set(hds[i], { opacity: 0 }, [p1, p2][i]);
    tl.fromTo(bls[i], { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.3, ease: 'back.out(1.8)', immediateRender: false }, t + 0.1);
    OM.sfx('pop', t + 0.12, { note: i + 1, gain: 0.45 });
  });
  // Cifra gigante.
  const num = $id('num');
  tl.fromTo(num, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.22, ease: 'back.out(2.2)', immediateRender: false }, PLAN.num[0])
    .set(num, { opacity: 0 }, PLAN.num[1]);
  OM.sfx('thud', PLAN.num[0] + 0.05, { gain: 0.5 });
  // Tachado: "Toda la culpa" y la raya roja cae en "otra".
  const tc = $id('tachado');
  tl.fromTo(tc, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.18, ease: 'power2.out', immediateRender: false }, PLAN.tachado[0])
    .fromTo(tc.querySelector('b'), { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: 'power3.out', immediateRender: false }, PLAN.tachado[1])
    .set(tc, { opacity: 0 }, PLAN.tachado[2]);
  // Destellos de luz cálida en los cambios de bloque (tapan el corte).
  const lk = $id('leak');
  PLAN.leaks.forEach((t) => {
    tl.fromTo(lk, { opacity: 0 }, { opacity: 0.95, duration: 0.16, ease: 'power1.in', immediateRender: false }, t - 0.16)
      .to(lk, { opacity: 0, duration: 0.4, ease: 'power2.out' }, t + 0.04);
    OM.sfx('whoosh', t - 0.1, { gain: 0.3 });
  });
  // Subtítulos: línea blanca pequeña y, debajo, la palabra que golpea grande (dorada; cursiva serif si tiene carga).
  const subs = $id('subs');
  const ventanas = [[PLAN.tachado[0], PLAN.tachado[2]], [PLAN.num[0], PLAN.num[1]], [p0, p3]];
  const hidden = (t) => ventanas.some(([a, b]) => t >= a - 0.05 && t < b);
  const plain = (w) => w.toLowerCase().replace(/[^\\p{L}\\p{N}]/gu, '');
  const blocks = []; let cur = [];
  words.forEach((w, i) => {
    if (hidden(w.start)) return;
    cur.push(w);
    const next = words[i + 1];
    const end = !next || /[.,?!:]$/.test(w.word) || cur.length === 3 || next.start - w.end > 0.25 || hidden(next.start)
      || PLAN.claves.includes(plain(w.word))
      || (cur.length >= 2 && PLAN.claves.includes(plain(next.word)));
    if (end) { blocks.push(cur); cur = []; }
  });
  blocks.forEach((bk, i) => {
    const el = document.createElement('div');
    el.className = 'sb';
    const txt = (w) => esc(w.word.replace(/[.,]$/, ''));
    const ki = bk.findIndex((w) => PLAN.claves.includes(plain(w.word)));
    if (ki < 0) el.innerHTML = `<div class="l1">${bk.map(txt).join(' ')}</div>`;
    else {
      const k = bk[ki], serif = PLAN.serif.includes(plain(k.word));
      el.innerHTML = (ki ? `<div class="l1">${bk.slice(0, ki).map(txt).join(' ')}</div>` : '')
        + `<div class="l2${serif ? ' s' : ''}">${txt(k)}</div>`;
    }
    subs.appendChild(el);
    const t0 = bk[0].start, nb = blocks[i + 1];
    const corte = ventanas.map(([a]) => a).filter((c) => c > t0).sort((a, b) => a - b)[0] ?? LEN;
    const t1 = Math.min(nb ? nb[0].start : LEN, bk[bk.length - 1].end + 0.6, corte);
    tl.fromTo(el, { opacity: 0, y: 16, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.14, ease: 'back.out(2)', immediateRender: false }, t0)
      .set(el, { opacity: 0 }, t1);
  });
  // Tarjeta de perfil: entra tras el destello y "Seguir" se pulsa en "sígueme".
  const fw = $id('follow');
  tl.fromTo(fw, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.35, ease: 'back.out(1.8)', immediateRender: false }, PLAN.follow[0])
    .fromTo(fw.querySelector('.b1'), { scale: 1 }, { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }, PLAN.follow[1])
    .set(fw.querySelector('.b1'), { opacity: 0 }, PLAN.follow[1] + 0.16).set(fw.querySelector('.b2'), { opacity: 1 }, PLAN.follow[1] + 0.16);
  OM.sfx('pop', PLAN.follow[1] + 0.05, { gain: 0.5, note: 5 });
  OM.music({ style: 'cinematic', drop: PLAN.num[0], ending: 'button' });
'''
