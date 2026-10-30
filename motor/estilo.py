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
  /* ---- recursos nuevos (30-10), sacados de los referentes de mi-estilo/recursos.md y vestidos con la marca ---- */
  /* sin z-index: va por orden debajo de titulares y subtítulos, que no se tiñen (30-10: con z-index 2 el dorado salía naranja) */
  .tinte { position: absolute; inset: 0; opacity: 0; mix-blend-mode: color; pointer-events: none; }
  .tinte.rojo { background: #E5322D; } .tinte.azul { background: #2E6BFF; } .tinte.verde { background: #2FA35B; }
  .tuit { position: absolute; left: 50%; top: 200px; width: 860px; margin-left: -430px; opacity: 0; z-index: 8; box-sizing: border-box;
    background: #070D16; border: 3px solid #2E6BFF; border-radius: 30px; padding: 24px 34px; box-shadow: 0 24px 60px #000a; }
  .tuit .cab { display: flex; align-items: center; gap: 20px; margin-bottom: 14px; }
  .tuit .av { width: 84px; height: 84px; border-radius: 50%; background: #1B2638; flex: none; display: grid; place-items: center;
    font: 400 40px/1 Anton, sans-serif; color: #8A96A8; }
  .tuit .nm { font: 800 40px/1.1 Inter, sans-serif; color: #fff; }
  .tuit .hn { font: 500 30px/1.2 Inter, sans-serif; color: #8A96A8; }
  .tuit .tx { font: 600 44px/1.22 Inter, sans-serif; color: #fff; }
  .tuit .tx b { color: #E0B83C; font-weight: 800; }
  .cort { position: absolute; inset: 0; z-index: 9; opacity: 0; overflow: hidden; pointer-events: none; }
  .cort .bd { position: absolute; inset: 0; background: #0E1F3A; border-right: 18px solid #2E6BFF; }   /* estilo.md: azul solo de filo */
  .cort .ws { position: absolute; left: 6%; right: 6%; top: 50%; transform: translateY(-50%); text-align: center; }
  .cort .w { display: block; font: 400 170px/0.98 Anton, sans-serif; color: #fff; text-transform: uppercase; opacity: 0; }
  .cort .w.k { color: #E0B83C; -webkit-text-stroke: 3px #070D16; paint-order: stroke fill; }
  .cont { position: absolute; left: 6%; top: 330px; z-index: 7; opacity: 0; display: flex; align-items: baseline; gap: 4px;
    background: #070D16E6; border: 3px solid #E0B83C; border-radius: 24px; padding: 8px 26px 12px; }
  .cont .n { font: 400 104px/1 Anton, sans-serif; color: #E0B83C; } .cont .d { font: 400 50px/1 Anton, sans-serif; color: #fff; }
  .marca { position: absolute; inset: 0; width: 1080px; height: 1920px; z-index: 6; opacity: 0; pointer-events: none; overflow: visible; }
  .marca .tr { fill: none; stroke: #E0B83C; stroke-width: 12; stroke-linecap: round; stroke-linejoin: round; filter: drop-shadow(0 4px 10px #000a); }
  .marca .cb { fill: #E0B83C; filter: drop-shadow(0 4px 10px #000a); }
  .marca text { font: 400 64px Anton, sans-serif; fill: #070D16; }
  .frz { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; }
  .frzt { position: absolute; left: 50%; top: 420px; transform: translateX(-50%); z-index: 7; opacity: 0; white-space: nowrap;
    background: #E0B83C; color: #070D16; font: 400 76px/1 Anton, sans-serif; padding: 16px 30px 12px; border-radius: 16px; box-shadow: 0 16px 40px #0009; }
  .flash { position: absolute; inset: 0; z-index: 9; background: #fff; opacity: 0; pointer-events: none; }
  /* segunda tanda (30-10) */
  .lst { position: absolute; left: 9%; right: 9%; top: 700px; z-index: 7; opacity: 0; text-shadow: 0 3px 14px #000c; }
  .lst .lt { font: 400 76px/1 Anton, sans-serif; color: #fff; text-transform: uppercase; margin-bottom: 26px; }
  .lst .li { display: flex; align-items: center; gap: 22px; font: 500 54px/1.15 Inter, sans-serif; color: #fff; margin-bottom: 20px; opacity: 0; }
  .lst .li b { font-weight: 800; color: #E0B83C; }
  .lst .li i { width: 26px; height: 26px; border-radius: 50%; background: #E0B83C; flex: none; box-shadow: 0 0 0 5px #E0B83C40; }
  .pil { position: absolute; left: 50%; top: 940px; transform: translateX(-50%); z-index: 7; opacity: 0; display: grid; place-items: center;
    background: #E0B83C; border-radius: 999px; padding: 14px 44px 10px; box-shadow: 0 14px 34px #0008; min-width: 200px; }
  .pil .pw { grid-area: 1 / 1; font: 400 72px/1 Anton, sans-serif; color: #0E1F3A; text-transform: uppercase; opacity: 0; white-space: nowrap; }
  .piz { position: absolute; left: 50%; top: 230px; width: 640px; height: 430px; margin-left: -320px; z-index: 7; opacity: 0; perspective: 900px; }
  .piz .pz3 { width: 100%; height: 100%; transform-origin: 50% 100%; }
  .piz svg { width: 100%; height: 100%; overflow: visible; filter: drop-shadow(0 20px 30px #000a); }
  .piz .pc { fill: #0E1F3A; stroke: #fff; stroke-width: 5; } .piz .pl { fill: none; stroke: #ffffffb0; stroke-width: 4; }
  .piz .jg { fill: #E0B83C; stroke: #070D16; stroke-width: 4; transform-box: fill-box; transform-origin: center; }
  .mapa { position: absolute; inset: 0; z-index: 7; opacity: 0; pointer-events: none; }
  .mapa svg { position: absolute; inset: 0; width: 1080px; height: 1920px; }
  .mapa .ml { fill: none; stroke: #E0B83C; stroke-width: 9; stroke-dasharray: 22 16; stroke-linecap: round; }
  .mapa .mk { fill: none; stroke: #fff; stroke-width: 40; }
  .mapa .mw { position: absolute; transform: translate(-50%, -50%); font: 700 60px/1 Inter, sans-serif; color: #fff; opacity: 0; white-space: nowrap;
    text-shadow: 0 4px 16px #000d; }
  .tcol { position: absolute; top: 480px; width: 250px; z-index: 6; display: flex; flex-direction: column; gap: 22px; }
  .tcol.der { right: 4%; } .tcol.izq { left: 4%; }
  .tcol .tc { width: 250px; height: 444px; border-radius: 24px; overflow: hidden; opacity: 0; border: 3px solid #E0B83C; box-shadow: 0 16px 36px #0009; }
  .tcol .tc video { width: 100%; height: 100%; object-fit: cover; }
  .logo { position: absolute; left: 0; right: 0; top: 880px; z-index: 8; opacity: 0; text-align: center; }
  .logo span { display: inline-block; font: italic 400 230px/1 Anton, sans-serif; color: #E0B83C; letter-spacing: .01em;
    -webkit-text-stroke: 4px #070D16; paint-order: stroke fill; text-shadow: 0 14px 40px #000c; }
  .logo .ch { position: absolute; top: -10px; bottom: -10px; width: 26px; margin-left: -13px; border-radius: 13px; opacity: 0;
    background: radial-gradient(#fffbe6, #ffd25a 45%, #ffb30000 75%); filter: blur(4px); }
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
  // Recursos nuevos (30-10): cada uno entra con su palabra y sale en su "out".
  PLAN.extras.forEach((x, i) => {
    const el = $id('x-' + i), t0 = x.in, t1 = x.out;
    const sale = (e) => tl.set(e, { opacity: 0 }, t1);
    if (x.tipo === 'tinte') {
      tl.fromTo(el, { opacity: 0 }, { opacity: 0.55, duration: 0.12, ease: 'power1.out', immediateRender: false }, t0)
        .to(el, { opacity: 0, duration: 0.15, ease: 'power1.in' }, t1 - 0.15);
    } else if (x.tipo === 'tuit' || x.tipo === 'contador') {
      tl.fromTo(el, { opacity: 0, y: -30, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: 'back.out(1.8)', immediateRender: false }, t0);
      sale(el);
    } else if (x.tipo === 'cortinilla') {   // banda que barre, palabras que caen una a una, y la banda se va
      const bd = el.querySelector('.bd'), ws = el.querySelectorAll('.w');
      tl.set(el, { opacity: 1 }, t0 - 0.22).fromTo(bd, { xPercent: -101 }, { xPercent: 0, duration: 0.22, ease: 'power3.in', immediateRender: false }, t0 - 0.22);
      const paso = Math.max(0.08, Math.min(0.2, (t1 - t0 - 0.35) / Math.max(1, ws.length)));
      ws.forEach((w, k) => tl.fromTo(w, { opacity: 0, y: 50, scale: 1.25 }, { opacity: 1, y: 0, scale: 1, duration: 0.16, ease: 'back.out(2)', immediateRender: false }, t0 + k * paso));
      tl.to(ws, { opacity: 0, duration: 0.1 }, t1 - 0.24).to(bd, { xPercent: 101, duration: 0.22, ease: 'power3.in' }, t1 - 0.22);
      sale(el);
    } else if (x.tipo === 'marca') {   // el trazo se dibuja; en la flecha, después la punta y el rótulo
      const tr = el.querySelectorAll('.tr'), cb = el.querySelectorAll('.cb, text');
      tl.set(el, { opacity: 1 }, t0).fromTo(tr, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.35, ease: 'power2.out', immediateRender: false }, t0);
      if (cb.length) tl.fromTo(cb, { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, t0 + 0.3);
      sale(el);
    } else if (x.tipo === 'congelado') {   // la imagen se para, destello blanco y rótulo; la voz sigue
      const img = $id('xi-' + i), fl = $id('xf-' + i);
      tl.set(img, { opacity: 1, filter: 'saturate(0.55) contrast(1.08)' }, t0)
        .fromTo(img, { scale: 1 }, { scale: 1.05, duration: t1 - t0, ease: 'none', immediateRender: false }, t0)
;
      if (fl) tl.fromTo(fl, { opacity: 0.85 }, { opacity: 0, duration: 0.3, ease: 'power2.out', immediateRender: false }, t0);
      if (el) { tl.fromTo(el, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.22, ease: 'back.out(2.2)', immediateRender: false }, t0 + 0.12); sale(el); }
      sale(img);
    } else if (x.tipo === 'lista') {
      tl.set(el, { opacity: 1 }, t0);
      el.querySelectorAll('.li').forEach((li, k) => tl.fromTo(li, { opacity: 0, x: -36 }, { opacity: 1, x: 0, duration: 0.22, ease: 'back.out(1.8)', immediateRender: false }, x.items[k]));
      sale(el);
    } else if (x.tipo === 'pildora') {
      const pw = el.querySelectorAll('.pw');
      tl.fromTo(el, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.22, ease: 'back.out(2)', immediateRender: false }, x.items[0]);
      pw.forEach((w, k) => {
        tl.set(w, { opacity: 1 }, x.items[k]);
        if (k) tl.set(pw[k - 1], { opacity: 0 }, x.items[k]).fromTo(el, { scale: 1.12 }, { scale: 1, duration: 0.18, ease: 'power2.out', immediateRender: false }, x.items[k]);
      });
      sale(el);
    } else if (x.tipo === 'pizarra') {   // se levanta en perspectiva, salen los jugadores y vuelve a tumbarse
      const p3 = el.querySelector('.pz3');
      tl.set(el, { opacity: 1 }, t0).fromTo(p3, { rotationX: 78, scale: 0.6, opacity: 0 }, { rotationX: 14, scale: 1, opacity: 1, duration: 0.55, ease: 'power3.out', immediateRender: false }, t0);
      el.querySelectorAll('.jg').forEach((j, k) => tl.fromTo(j, { scale: 0 }, { scale: 1, duration: 0.2, ease: 'back.out(3)', immediateRender: false }, x.items[k]));
      tl.to(p3, { rotationX: 78, opacity: 0, duration: 0.35, ease: 'power2.in' }, t1 - 0.35);
      sale(el);
    } else if (x.tipo === 'mapa') {   // cada palabra al decirla, y la línea llega hasta ella
      const mk = el.querySelector('.mk'), fr = JSON.parse(el.dataset.f);
      tl.set(el, { opacity: 1 }, t0);
      el.querySelectorAll('.mw').forEach((w, k) => {
        tl.fromTo(w, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.2, ease: 'power2.out', immediateRender: false }, x.items[k]);
        if (k) tl.fromTo(mk, { strokeDashoffset: fr[k - 1] }, { strokeDashoffset: fr[k], duration: 0.3, ease: 'power1.inOut', immediateRender: false }, x.items[k] - 0.3);
      });
      sale(el);
    } else if (x.tipo === 'tarjetas') {
      el.querySelectorAll('.tc').forEach((c, k) => tl.fromTo(c, { opacity: 0, scale: 0.85, y: 30 }, { opacity: 1, scale: 1, y: 0, duration: 0.28, ease: 'back.out(1.6)', immediateRender: false }, x.items[k]));
      tl.set(el.querySelectorAll('.tc'), { opacity: 0 }, t1);
    } else if (x.tipo === 'barrido') {   // el plano entra arrastrado y desenfocado
      tl.fromTo(tw, { filter: 'blur(18px)', x: -90 }, { filter: 'blur(0px)', x: 0, duration: 0.24, ease: 'power3.out', immediateRender: false }, t0)
        .set(tw, { filter: 'none' }, t0 + 0.25);
    } else if (x.tipo === 'logo') {   // se revela de izquierda a derecha con una chispa en el borde
      const sp = el.querySelector('span'), ch = el.querySelector('.ch');
      tl.set(el, { opacity: 1 }, t0)
        .fromTo(sp, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: 0.4, ease: 'power2.inOut', immediateRender: false }, t0)
        .fromTo(ch, { left: '22%', opacity: 1 }, { left: '78%', duration: 0.4, ease: 'power2.inOut', immediateRender: false }, t0)
        .to(ch, { opacity: 0, duration: 0.15 }, t0 + 0.4);
      sale(el);
    } else if (x.tipo === 'detras') {
      tl.set(el, { opacity: 1 }, t0);
      sale(el);
    }
  });
  // Tarjeta de perfil: entra tras el destello y "Seguir" se pulsa en "sígueme".
  const fw = $id('follow');
  tl.fromTo(fw, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.35, ease: 'back.out(1.8)', immediateRender: false }, PLAN.follow[0])
    .fromTo(fw.querySelector('.b1'), { scale: 1 }, { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }, PLAN.follow[1])
    .set(fw.querySelector('.b1'), { opacity: 0 }, PLAN.follow[1] + 0.16).set(fw.querySelector('.b2'), { opacity: 1 }, PLAN.follow[1] + 0.16);
  OM.sfx('pop', PLAN.follow[1] + 0.05, { gain: 0.5, note: 5 });
  OM.music({ style: 'cinematic', drop: PLAN.num[0], ending: 'button' });
'''
