// WORLD DESK · The Shenzhen Summit — a Broadcast News Package film (19 Nov 2026 Trump–Xi–Putin summit)
// Canvas 2D, deterministic render(t). 120 BPM grid, beat 0 = 6.0 s (end of the sting). Shot list: TREATMENT.md.
// Picture layer: real file photos of the leaders (tagged FILE PHOTO) + AI-generated fictional people (tagged ILLUSTRATION).
const W = 1920, H = 1080, DUR = 72.0;
const cv = document.getElementById('out'); const ctx = cv.getContext('2d');

const C = {
  ink: '#121417', ink2: '#1B1E23', ink3: '#22262C', line: '#454B55',
  lemon: '#F2CF1D', lemonL: '#F8DE4A', lemonD: '#D8B30C', gold: '#D4B064', olive: '#6E5A1E',
  paper: '#F4F1E8', white: '#FFFFFF', grey: '#C9CCD2', grey2: '#7D838D', red: '#E5484D',
};
const F = { b8: s => `800 ${s}px Barlow`, b6: s => `600 ${s}px Barlow`, b6i: s => `italic 600 ${s}px Barlow`, mono: s => `500 ${s}px Plex` };

// —— helpers ——
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const eo = x => 1 - Math.pow(1 - x, 3);
const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const back = (x, s = 1.70158) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
function hash(n) { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
const IM = {};
function loadImg(src) { return new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => no(src); i.src = src; }); }

let TX = [];
function text(s, x, y, font, color, align = 'left', ls = 0, id = null, pass = false) {
  ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
  ctx.letterSpacing = ls + 'px'; ctx.fillText(s, x, y);
  const w = ctx.measureText(s).width; ctx.letterSpacing = '0px';
  if (id && ctx.globalAlpha > .5) { const m = ctx.getTransform(); const x0 = align === 'left' ? x : align === 'right' ? x - w : x - w / 2; const fs = parseInt(font.match(/(\d+)px/)[1]);
    const p0 = m.transformPoint({ x: x0, y: y - fs }), p1 = m.transformPoint({ x: x0 + w, y: y + 8 });
    TX.push({ id, text: s, pass, x0: Math.min(p0.x, p1.x), y0: Math.min(p0.y, p1.y), x1: Math.max(p0.x, p1.x), y1: Math.max(p0.y, p1.y) }); }
  return w;
}
function tw(s, font, ls = 0) { ctx.font = font; ctx.letterSpacing = ls + 'px'; const w = ctx.measureText(s).width; ctx.letterSpacing = '0px'; return w; }

// cover-fit: source point (fx,fy) at the rect centre, scale s (clamped so the rect is always covered)
function photo(img, fx, fy, s, rx = 0, ry = 0, rw = W, rh = H) {
  s = Math.max(s, rw / img.width, rh / img.height);
  let ox = rx + rw / 2 - fx * s, oy = ry + rh / 2 - fy * s;
  ox = Math.min(rx, Math.max(rx + rw - img.width * s, ox)); oy = Math.min(ry, Math.max(ry + rh - img.height * s, oy));
  ctx.save(); ctx.beginPath(); ctx.rect(rx, ry, rw, rh); ctx.clip();
  ctx.drawImage(img, ox, oy, img.width * s, img.height * s); ctx.restore();
}
function vignette(a = .5) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .95);
  g.addColorStop(0, 'rgba(8,9,11,0)'); g.addColorStop(1, `rgba(8,9,11,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
const GR = [];
function makeGrain() {
  for (let k = 0; k < 6; k++) {
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); const d = g.createImageData(256, 256);
    for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (hash(i * .37 + k * 9.1) + hash(i * .11 + k) - 1) * 150; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    g.putImageData(d, 0, 0); GR.push(c);
  }
}
function grain(t, a = .06) {
  const f = Math.floor(t * 24), c = GR[f % GR.length];
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = a;
  const ox = -Math.floor(hash(f) * 256), oy = -Math.floor(hash(f + 7) * 256);
  for (let x = ox; x < W; x += 256) for (let y = oy; y < H; y += 256) ctx.drawImage(c, x, y);
  ctx.restore();
}
// a photoreal plate: picture, soft vignette, grain (package layers are never grained)
function plateShot(img, fx, fy, s, t, dark = 0) {
  photo(img, fx, fy, s); if (dark) { ctx.fillStyle = `rgba(12,13,16,${dark})`; ctx.fillRect(0, 0, W, H); }
  const g = ctx.createLinearGradient(0, H * .55, 0, H); g.addColorStop(0, 'rgba(12,13,16,0)'); g.addColorStop(1, 'rgba(12,13,16,.55)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  vignette(.45); grain(t);
}

// —— brand plate: lemon parallelogram, ink + gold bars, WORLD dropping in ——
function plate(cx, cy, s, glint = -1, drop = 1) {
  const w = 520 * s, h = 180 * s, k = h * .28;
  ctx.save(); ctx.translate(cx, cy);
  const path = new Path2D(); path.moveTo(-w / 2 + k, -h / 2); path.lineTo(w / 2 + k, -h / 2); path.lineTo(w / 2 - k, h / 2); path.lineTo(-w / 2 - k, h / 2); path.closePath();
  const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2); g.addColorStop(0, C.lemonL); g.addColorStop(1, C.lemonD);
  ctx.fillStyle = g; ctx.fill(path); ctx.save(); ctx.clip(path);
  const gx = -w / 2 - k;
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.moveTo(gx + 2 * k, -h / 2); ctx.lineTo(gx + 2 * k + w * .085, -h / 2); ctx.lineTo(gx + w * .085, h / 2); ctx.lineTo(gx, h / 2); ctx.fill();
  ctx.fillStyle = C.gold; ctx.beginPath(); ctx.moveTo(gx + 2 * k + w * .085, -h / 2); ctx.lineTo(gx + 2 * k + w * .11, -h / 2); ctx.lineTo(gx + w * .11, h / 2); ctx.lineTo(gx + w * .085, h / 2); ctx.fill();
  ctx.font = F.b8(h * .78); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  let x = -w * .27;
  ['W', 'O', 'R', 'L', 'D'].forEach((L, i) => {
    const d = clamp(drop * 5 - i); const yy = h * .28 + (1 - eo(d)) * -h * 1.1;
    ctx.save(); ctx.globalAlpha *= clamp(d * 3); ctx.fillStyle = C.ink; ctx.fillText(L, x, yy); ctx.restore();
    x += ctx.measureText(L).width - h * .01;
  });
  if (glint >= 0 && glint <= 1) {
    const gx2 = lerp(-w, w, glint); const gg = ctx.createLinearGradient(gx2 - 80 * s, 0, gx2 + 80 * s, 0);
    gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(.5, 'rgba(255,255,255,.6)'); gg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = gg; ctx.fillRect(-w, -h, w * 2, h * 2);
  }
  ctx.restore(); ctx.restore();
}
function wordmark(x, y, size, id = null) {
  const parts = [['WORLD ', C.white], ['DESK', C.lemon]], ls = size * .14;
  const tot = parts.reduce((a, [s]) => a + tw(s, F.b8(size), ls), 0);
  let cx = x - tot / 2; for (const [s, c] of parts) cx += text(s, cx, y, F.b8(size), c, 'left', ls);
  if (id) TX.push({ id, text: 'WORLD DESK', x0: x - tot / 2, y0: y - size, x1: x + tot / 2, y1: y + 8 });
}

// ============ package layers (drawn per picture, inside wipes) ============
const STRAP = { out: 67.5, items: [
  { a: 6.0, tab: 'SUMMIT', l1: 'TRUMP, XI AND PUTIN MEET IN SHENZHEN', l2: 'FIRST-EVER THREE-WAY SUMMIT · ON THE SIDELINES OF APEC' },
  { a: 14.5, tab: 'LEADERS', l1: 'THREE LEADERS, ONE TABLE', l2: 'UNITED STATES · CHINA · RUSSIA' },
  { a: 21.0, tab: 'DECLARATION', l1: 'A JOINT “PEACE DECLARATION”', l2: 'ENERGY · NUCLEAR RISK · STABILITY · INTERNATIONAL COURTS' },
  { a: 34.0, tab: 'ANALYSIS', l1: 'WHAT THE DECLARATION LEAVES OUT', l2: 'NO ARMS-CONTROL TIMETABLE · UKRAINE NOT MENTIONED, REPORTS SAY' },
  { a: 45.0, tab: 'PROFILE', l1: 'XI JINPING', l2: 'PRESIDENT OF THE PEOPLE’S REPUBLIC OF CHINA' },
  { a: 51.5, tab: 'REACTION', l1: 'THE WORLD IS WATCHING', l2: 'WILL THE WORDS BECOME ACTION?' },
  { a: 60.0, tab: 'WHAT NEXT', l1: 'AFTER SHENZHEN: WHAT COMES NEXT', l2: 'WORLD DESK · 19 NOVEMBER 2026' },
] };
function strap(t) {
  if (t < STRAP.items[0].a || t >= STRAP.out) return;
  let S = STRAP.items[0]; for (const it of STRAP.items) if (t >= it.a) S = it;
  const x0 = 96, ty = 856, by = 904, bh = 104, bw = 1250;
  ctx.save();
  ctx.fillStyle = 'rgba(0,0,0,.3)'; ctx.fillRect(x0 + 8, by + 8, bw, bh);
  ctx.fillStyle = C.paper; ctx.fillRect(x0, by, bw, bh);
  ctx.fillStyle = C.lemon; ctx.fillRect(x0, by, 14, bh);
  ctx.fillStyle = C.ink; ctx.fillRect(x0 + bw, by, 120, bh); ctx.fillStyle = C.lemon; ctx.fillRect(x0 + bw, by, 120, 6);
  text('WD', x0 + bw + 60, by + 72, F.b8(48), C.lemon, 'center', 2);
  ctx.save(); ctx.beginPath(); ctx.rect(x0 + 14, by, bw - 14, bh); ctx.clip();
  text(S.l1, x0 + 44, by + 58, F.b8(52), C.ink, 'left', 1, 'strap'); text(S.l2, x0 + 46, by + 92, F.b6(26), C.olive, 'left', 1.5, 'strape');
  ctx.restore();
  const tabW = 40 + tw(S.tab, F.b8(30), 3);
  ctx.fillStyle = C.lemon; ctx.fillRect(x0, ty, tabW, by - ty);
  text(S.tab, x0 + 20, ty + 37, F.b8(30), C.ink, 'left', 3);
  ctx.restore();
}
const TAGS = [
  [0, 4.5, 'ILLUSTRATION', 'AI-GENERATED · FICTIONAL PERSON'],
  [14.5, 21.0, 'FILE PHOTOS', 'WHITE HOUSE 2025 · KREMLIN 2024'],
  [21.0, 34.0, 'ILLUSTRATION', 'AI-GENERATED ROOM · NOT THE VENUE'],
  [45.0, 51.5, 'FILE PHOTO', 'KREMLIN.RU · MAY 2024'],
  [51.5, 60.0, 'ILLUSTRATION', 'AI-GENERATED · FICTIONAL PEOPLE'],
  [60.0, 67.5, 'ILLUSTRATION', 'AI-GENERATED · FICTIONAL PERSON'],
];
function cornerTag(t) {
  const A = TAGS.find(r => t >= r[0] && t < r[1]); if (!A) return;
  const x = 96, y = 56, h = 64, w = 30 + Math.max(tw(A[2], F.mono(18), 2), tw(A[3], F.b6(22), 1)) + 30;
  ctx.fillStyle = 'rgba(18,20,23,.82)'; ctx.fillRect(x, y, w, h);
  ctx.fillStyle = C.gold; ctx.fillRect(x, y, 8, h);
  text(A[2], x + 26, y + 27, F.mono(18), C.gold, 'left', 2, 'tag');
  text(A[3], x + 26, y + 53, F.b6(22), C.white, 'left', 1, 'tag2');
}
const SRC = [
  [6.0, 14.5, 'REPORTED BY AL JAZEERA · REUTERS'],
  [14.5, 21.0, 'PHOTOS: WHITE HOUSE · KREMLIN.RU'],
  [21.0, 34.0, 'REPORTED BY AL JAZEERA · REUTERS'],
  [34.0, 45.0, 'REPORTED BY AL JAZEERA · FOX NEWS'],
  [45.0, 51.5, 'QUOTED BY AL JAZEERA, 19 NOV'],
  [60.0, 67.5, 'QUOTED BY AL JAZEERA, 19 NOV'],
];
function source(t) {
  const R = SRC.find(r => t >= r[0] && t < r[1]); if (!R) return;
  ctx.save(); ctx.globalAlpha = .75; text(R[2], 1836, 1040, F.mono(14), C.paper, 'right', .5); ctx.restore();
}
function bug(t) {
  if (t < 5.95 || t > 67.4) return;
  ctx.save(); ctx.globalAlpha = .95; plate(1739, 86, .327, -1, 1); ctx.restore();
}

// ============ backgrounds ============
function studioBg(t) {
  ctx.fillStyle = C.ink; ctx.fillRect(0, 0, W, H);
  const rg = ctx.createRadialGradient(1300, 380, 60, 1300, 380, 1100); rg.addColorStop(0, 'rgba(242,207,29,.14)'); rg.addColorStop(1, 'rgba(242,207,29,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 7; i++) {
    const x = ((i * 380 + t * (30 + i * 6)) % 2600) - 400, w = 40 + hash(i) * 120;
    ctx.fillStyle = `rgba(242,207,29,${.022 + hash(i + 9) * .03})`;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + w, 0); ctx.lineTo(x + w - 500, H); ctx.lineTo(x - 500, H); ctx.fill();
  }
  ctx.fillStyle = 'rgba(244,241,232,.05)';
  for (let x = 40 - (t * 12) % 48; x < W; x += 48) for (let y = 24; y < H; y += 48) ctx.fillRect(x, y, 2, 2);
}
function stamp(t, t0, label, cx, cy, rot = -.12, size = 64, big = false) {
  const k = seg(t, t0, t0 + .16); if (k <= 0) return;
  const s = 1 + .9 * (1 - eo(k)); const w = tw(label, F.b8(size), 3) + 70, h = size + 44;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(s, s); ctx.globalAlpha = clamp(k * 3);
  if (big) { ctx.fillStyle = C.lemon; ctx.fillRect(-w / 2, -h / 2, w, h); text(label, 0, size * .36, F.b8(size), C.ink, 'center', 3, 'stamp'); }
  else { ctx.fillStyle = C.ink; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.strokeStyle = C.lemon; ctx.lineWidth = 5; ctx.strokeRect(-w / 2 + 6, -h / 2 + 6, w - 12, h - 12); ctx.lineWidth = 2; ctx.strokeRect(-w / 2 + 14, -h / 2 + 14, w - 28, h - 28); text(label, 0, size * .36, F.b8(size), C.lemon, 'center', 3, 'stamp'); }
  ctx.restore();
  const r = seg(t, t0 + .16, t0 + .6); if (r > 0 && r < 1) { ctx.strokeStyle = `rgba(242,207,29,${(1 - r) * .8})`; ctx.lineWidth = 4; ctx.beginPath(); ctx.ellipse(cx, cy, w * .6 + r * 300, h * .7 + r * 140, rot, 0, Math.PI * 2); ctx.stroke(); }
}
const pushUp = (t, a, y, h, fn) => { const k = eo(seg(t, a, a + .3)); if (k <= 0) return; ctx.save(); ctx.beginPath(); ctx.rect(0, y - h, W, h + 16); ctx.clip(); ctx.translate(0, (1 - k) * (h + 30)); fn(); ctx.restore(); };

// ============ S1 cold open: a woman reads the alert ============
function shotCold(t, bookend = false) {
  const s = bookend ? lerp(1.04, .9, eio(seg(t, 60.0, 67.5))) : lerp(.80, .90, seg(t, 0, 4.5));
  plateShot(IM.street, bookend ? 1500 : 820, 640, s, t, bookend ? .1 : 0);
  if (!bookend) {   // the alert she is reading: a lower-left card slides up
    const k = eo(seg(t, 1.0, 1.4)); if (k <= 0) return;
    const x = 120, y = 760 + (1 - k) * 60, w = 820, h = 170;
    ctx.save(); ctx.globalAlpha = k;
    ctx.fillStyle = 'rgba(18,20,23,.9)'; ctx.fillRect(x, y, w, h); ctx.fillStyle = C.lemon; ctx.fillRect(x, y, w, 6);
    text('NEWS ALERT · 19 NOV 2026 · SHENZHEN', x + 32, y + 52, F.mono(20), C.gold, 'left', 3, 'alert0');
    text('Trump, Xi and Putin meet', x + 30, y + 104, F.b8(48), C.white, 'left', 1, 'alert1');
    text('for the first time — together', x + 30, y + 148, F.b6(38), C.grey, 'left', 1, 'alert2');
    ctx.restore();
  } else {   // bookend: Trump's line on an ink panel
    const k = eo(seg(t, 60.1, 60.5)), x = lerp(W, 1140, k), y = 250, w = 700, h = 470;
    ctx.save(); ctx.fillStyle = 'rgba(18,20,23,.9)'; ctx.fillRect(x, y, w, h); ctx.fillStyle = C.lemon; ctx.fillRect(x, y, 8, h);
    text('“', x + 40, y + 150, F.b8(170), C.lemon);
    pushUp(t, 60.4, y + 210, 60, () => text('No peace was ever', x + 48, y + 210, F.b8(64), C.white, 'left', 1, 'bq1'));
    pushUp(t, 60.55, y + 282, 60, () => text('forged by declining', x + 48, y + 282, F.b8(64), C.white, 'left', 1, 'bq2'));
    pushUp(t, 60.7, y + 354, 60, () => text('opportunities.”', x + 48, y + 354, F.b8(64), C.white, 'left', 1, 'bq3'));
    const a = seg(t, 63.5, 63.9); ctx.globalAlpha = a;
    ctx.fillStyle = C.gold; ctx.fillRect(x + 48, y + 388, 220 * eo(a), 3);
    text('DONALD TRUMP', x + 48, y + 428, F.b8(32), C.lemon, 'left', 3, 'bqn');
    text('SHENZHEN · 19 NOV 2026', x + 270, y + 428, F.mono(18), C.grey, 'left', 2);
    ctx.restore();
  }
}

// ============ S2 sting ============
function shotSting(t) {
  studioBg(t + 4.5);
  [[.04, .3, 22, -60], [.1, .36, 8, 40]].forEach(([a, b, h, dy]) => {
    const k = seg(t, a, b); if (k <= 0 || k >= 1) return;
    ctx.save(); ctx.translate(960, 470 + dy); ctx.rotate(-.14); const x = lerp(-1900, 1900, eio(k)); ctx.fillStyle = C.lemon; ctx.fillRect(x - 700, -h / 2, 1400, h); ctx.restore();
  });
}
function stingLogo(t) {
  if (t > 1.5 || t < 0) return;
  const k = seg(t, .16, .42), fly = eio(seg(t, 1.12, 1.45));
  const shake = t > .42 && t < .7 ? Math.sin(t * 90) * 14 * (1 - seg(t, .42, .7)) : 0;
  const cx = lerp(960, 1739, fly) + shake, cy = lerp(450, 86, fly), s = lerp(back(k, 2.2), .327, fly);
  if (k > 0) { ctx.save(); ctx.translate(cx, cy); ctx.rotate((1 - eo(k)) * -.12 * (1 - fly)); ctx.translate(-cx, -cy); plate(cx, cy, s, seg(t, .85, 1.12) || -1, seg(t, .3, .7)); ctx.restore(); }
  const r = seg(t, .42, .8); if (r > 0 && r < 1) { ctx.strokeStyle = `rgba(242,207,29,${1 - r})`; ctx.lineWidth = 6 * (1 - r) + 1; ctx.beginPath(); ctx.ellipse(960, 450, 300 + r * 700, 120 + r * 300, 0, 0, Math.PI * 2); ctx.stroke(); }
  const wa = seg(t, .5, .8), wo = 1 - seg(t, 1.05, 1.18);
  if (wa > 0 && wo > 0) {
    ctx.save(); ctx.globalAlpha = wo; ctx.beginPath(); ctx.rect(960 - 520 * eo(wa), 560, 1040 * eo(wa), 160); ctx.clip();
    wordmark(960, 640, 70); text('SPECIAL REPORT · 19 NOV 2026', 960, 690, F.mono(22), C.gold, 'center', 3); ctx.restore();
  }
}

// ============ S3 dateline: split-flap board ============
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
function flapTile(x, y, w, h, ch, t0, t, i) {
  ctx.fillStyle = C.ink3; ctx.fillRect(x, y, w, h);
  ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(x, y + h / 2 - 2, w, 4);
  if (ch === ' ') return;
  const k = seg(t, t0, t0 + .34); if (k <= 0) return;
  const n = Math.floor(k * 5); const shown = k >= 1 ? ch : GLYPHS[Math.floor(hash(i * 7 + n) * GLYPHS.length)];
  const sub = (k * 5) % 1, sq = k >= 1 ? 1 : Math.abs(Math.cos(sub * Math.PI));
  ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(1, Math.max(.05, sq));
  ctx.font = F.b8(h * .78); ctx.fillStyle = k >= 1 ? C.white : C.grey; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(shown, 0, h * .04); ctx.restore();
  ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(x, y + h / 2 - 1, w, 2);
}
function board(t, str, x, y, tw_, th, t0, id, base) {
  for (let i = 0; i < str.length; i++) flapTile(x + i * (tw_ + 10), y, tw_, th, str[i], t0 + i * .06, t, base + i);
  if (t > t0 + str.length * .06 + .35) TX.push({ id, text: str, x0: x, y0: y, x1: x + str.length * (tw_ + 10), y1: y + th });
}
function shotDate(t) {
  studioBg(t);
  const z = lerp(1.05, 1.0, eo(seg(t, 5.8, 14.5)));
  ctx.save(); ctx.translate(960, 440); ctx.scale(z, z); ctx.translate(-960, -440);
  ctx.globalAlpha = eo(seg(t, 6.0, 6.3));
  text('APEC SIDELINES · SHENZHEN, CHINA · THU 19 NOV 2026', 150, 150, F.mono(24), C.gold, 'left', 4, 'eyeD');
  ctx.globalAlpha = 1;
  board(t, '19 NOV 2026', 150, 200, 96, 140, 6.6, 'bd1', 0);
  board(t, 'SHENZHEN', 150, 380, 96, 140, 7.8, 'bd2', 40);
  // three countries push up
  const cs = [['UNITED STATES', 9.3], ['CHINA', 10.1], ['RUSSIA', 10.6]]; let x = 154;
  cs.forEach(([c, a], i) => {
    pushUp(t, a, 660, 70, () => text(c, x, 660, F.b8(72), i === 1 ? C.lemon : C.white, 'left', 3, 'cty' + i));
    x += tw(c, F.b8(72), 3) + 30;
    if (i < 2) { ctx.globalAlpha = seg(t, a + .2, a + .4); ctx.fillStyle = C.gold; ctx.fillRect(x - 22, 630, 10, 10); ctx.globalAlpha = 1; x += 10; }
  });
  ctx.restore();
  stamp(t, 12.0, 'FIRST-EVER', 1590, 330, -.1, 70, true);
  const rk = seg(t, 11.5, 11.9);
  if (rk > 0) { ctx.globalAlpha = rk; text('THREE-WAY SUMMIT', 1590, 470, F.b8(44), C.white, 'center', 4, 'tws'); ctx.globalAlpha = 1; }
}

// ============ S4 who: three real file portraits ============
const LEAD = [
  { img: 'trump', s: .95, fx: 300, fy: 360, name: 'DONALD TRUMP', role: 'PRESIDENT · UNITED STATES', a: 14.75 },
  { img: 'xi', s: 1.15, fx: 260, fy: 300, name: 'XI JINPING', role: 'PRESIDENT · CHINA', a: 15.95 },
  { img: 'putin', s: 1.0, fx: 250, fy: 330, name: 'VLADIMIR PUTIN', role: 'PRESIDENT · RUSSIA', a: 17.15 },
];
function shotWho(t) {
  studioBg(t);
  const drift = lerp(24, -24, seg(t, 14.2, 21.0));
  LEAD.forEach((L, i) => {
    const k = seg(t, L.a, L.a + .35); if (k <= 0) return;
    const cw = 500, ch = 600, x = 150 + i * 560 + drift * (1 + i * .3), y = 120 + (1 - eo(k)) * 120;
    ctx.save(); ctx.globalAlpha = clamp(k * 2.5);
    ctx.fillStyle = 'rgba(0,0,0,.4)'; ctx.fillRect(x + 12, y + 12, cw, ch);
    photo(IM[L.img], L.fx, L.fy, lerp(L.s, L.s * .94, seg(t, L.a, 21)), x, y, cw, ch - 120);
    ctx.fillStyle = C.ink2; ctx.fillRect(x, y + ch - 120, cw, 120); ctx.fillStyle = C.lemon; ctx.fillRect(x, y + ch - 120, cw, 6);
    text(L.name, x + 28, y + ch - 56, F.b8(50), C.white, 'left', 2, 'nm' + i);
    text(L.role, x + 30, y + ch - 20, F.mono(18), C.gold, 'left', 2, 'rl' + i);
    // light sweep on arrival
    const sw = seg(t, L.a + .1, L.a + .55); if (sw > 0 && sw < 1) { const gx = x + cw * eio(sw); const g = ctx.createLinearGradient(gx - 160, 0, gx, 0); g.addColorStop(0, 'rgba(242,207,29,0)'); g.addColorStop(1, 'rgba(242,207,29,.25)'); ctx.fillStyle = g; ctx.fillRect(Math.max(x, gx - 160), y, Math.min(160, gx - x), ch); }
    ctx.restore();
  });
  // Trump's line, as a chip under the cards
  const q = eo(seg(t, 17.3, 17.6)); if (q > 0) {
    const s = '“WE’RE MAKING HISTORY” — TRUMP', w = tw(s, F.b8(40), 2) + 60, x = 960 - w / 2 + drift, y = 752;
    ctx.save(); ctx.globalAlpha = q; ctx.fillStyle = C.lemon; ctx.fillRect(x, y, w * q, 72);
    ctx.beginPath(); ctx.rect(x, y, w * q, 72); ctx.clip(); text(s, x + 30, y + 52, F.b8(40), C.ink, 'left', 2, 'hist'); ctx.restore();
  }
}

// ============ S5 the declaration ============
const DECL = [['STABLE ENERGY FLOWS', '', 25.0], ['DIALOGUE ON NUCLEAR RISKS', 'AND PREVENTING PROLIFERATION', 27.0], ['STRATEGIC STABILITY', 'AND INTERNATIONAL SECURITY', 29.0], ['COURTS MUST NOT', '“ABUSE THEIR POSITIONS”', 32.5]];
function shotDecl(t) {
  const z = lerp(.84, .9, seg(t, 20.7, 34.0));
  plateShot(IM.room, 1200, 620, z, t, .25);
  const g = ctx.createLinearGradient(0, 0, 1100, 0); g.addColorStop(0, 'rgba(14,16,19,.9)'); g.addColorStop(1, 'rgba(14,16,19,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // left: title
  ctx.globalAlpha = eo(seg(t, 21.0, 21.3)); text('SHENZHEN · 19 NOV 2026', 150, 230, F.mono(24), C.gold, 'left', 4, 'eyeP'); ctx.globalAlpha = 1;
  pushUp(t, 21.1, 360, 120, () => text('WHAT THEY', 146, 360, F.b8(128), C.white, 'left', 3, 'wt1'));
  pushUp(t, 21.3, 490, 120, () => text('SIGNED', 146, 490, F.b8(128), C.lemon, 'left', 3, 'wt2'));
  const cnt = DECL.filter(d => t >= d[2]).length;
  if (cnt > 0) text(`${cnt} / 4 POINTS`, 150, 560, F.mono(24), C.grey, 'left', 4);
  // right: the document flies in and is pushed into
  const k = seg(t, 21.0, 21.55); if (k <= 0) return;
  const pz = lerp(1.0, 1.05, seg(t, 21.6, 34));
  const dw = 760, dh = 700, cx = 1340, cy = 450;
  ctx.save(); ctx.translate(lerp(1700, cx, eo(k)), lerp(150, cy, eo(k))); ctx.rotate((1 - eo(k)) * .35 - .02); const sc = lerp(.15, 1, eo(k)) * pz; ctx.scale(sc, sc);
  ctx.fillStyle = 'rgba(0,0,0,.45)'; ctx.fillRect(-dw / 2 + 16, -dh / 2 + 16, dw, dh);
  ctx.fillStyle = C.paper; ctx.fillRect(-dw / 2, -dh / 2, dw, dh);
  ctx.fillStyle = C.ink; ctx.fillRect(-dw / 2, -dh / 2, dw, 110); ctx.fillStyle = C.lemon; ctx.fillRect(-dw / 2, -dh / 2 + 110, dw, 6);
  text('JOINT PEACE DECLARATION', -dw / 2 + 40, -dh / 2 + 62, F.b8(46), C.white, 'left', 3, 'dt');
  text('UNITED STATES · CHINA · RUSSIA', -dw / 2 + 42, -dh / 2 + 94, F.mono(18), C.gold, 'left', 2);
  DECL.forEach(([a, b, at], i) => {
    const y = -dh / 2 + 160 + i * 132, x = -dw / 2 + 40;
    ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.strokeRect(x, y + 6, 56, 56);
    text(a, x + 86, y + 44, F.b8(40), t >= at - .4 ? C.ink : '#9A968C', 'left', 1.5, 'dr' + i);
    if (b) text(b, x + 88, y + 82, F.b6(26), t >= at - .4 ? C.olive : '#B5B0A4', 'left', 1.5, 'drb' + i);
    const ck = seg(t, at, at + .2);
    if (ck > 0) { ctx.save(); ctx.translate(x + 28, y + 34); const s = back(ck, 2.6); ctx.scale(s, s); ctx.strokeStyle = C.lemonD; ctx.lineWidth = 10; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(-16, 2); ctx.lineTo(-4, 15); ctx.lineTo(20, -16); ctx.stroke(); ctx.restore(); }
    if (i < 3) { ctx.fillStyle = 'rgba(18,20,23,.12)'; ctx.fillRect(x, y + 114, dw - 80, 2); }
  });
  ctx.restore();
}

// ============ S6 what it left out ============
const OMIT = [['A TIMETABLE FOR ARMS-CONTROL TALKS', 'NO PLANS ANNOUNCED', 35.5, 37.6], ['RUSSIA’S WAR IN UKRAINE', 'NOT MENTIONED, REPORTS SAY', 38.4, 41.0]];
function shotOmit(t) {
  studioBg(t * .5);
  ctx.fillStyle = 'rgba(12,13,16,.35)'; ctx.fillRect(0, 0, W, H);
  const sh = t > 42.5 && t < 42.9 ? Math.sin(t * 95) * 12 * (1 - seg(t, 42.5, 42.9)) : 0;
  ctx.save(); ctx.translate(sh, 0);
  ctx.globalAlpha = eo(seg(t, 34.0, 34.3)); text('NOT IN THE TEXT', 150, 200, F.mono(24), C.gold, 'left', 5, 'eyeO'); ctx.globalAlpha = 1;
  pushUp(t, 34.1, 320, 120, () => text('WHAT IT LEFT OUT', 146, 320, F.b8(124), C.white, 'left', 3, 'lo'));
  OMIT.forEach(([a, b, at, st], i) => {
    const k = seg(t, at, at + .3); if (k <= 0) return;
    const y = 400 + i * 190, x = 150, w = 1300, h = 150, sy = back(k, 2.0);
    ctx.save(); ctx.translate(0, y); ctx.scale(1, Math.max(.02, sy)); ctx.translate(0, -y);
    ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillRect(x + 10, y + 10, w, h);
    ctx.fillStyle = C.ink2; ctx.fillRect(x, y, w, h); ctx.fillStyle = C.red; ctx.fillRect(x, y, 140, h);
    ctx.strokeStyle = C.white; ctx.lineWidth = 12; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x + 44, y + 44); ctx.lineTo(x + 96, y + 106); ctx.moveTo(x + 96, y + 44); ctx.lineTo(x + 44, y + 106); ctx.stroke();
    text(a, x + 176, y + 74, F.b8(54), C.white, 'left', 2, 'om' + i);
    text(b, x + 178, y + 118, F.mono(22), C.gold, 'left', 3, 'omb' + i);
    const s2 = eio(seg(t, st, st + .45)); if (s2 > 0) { const ww = tw(a, F.b8(54), 2); ctx.fillStyle = C.red; ctx.fillRect(x + 172, y + 54, (ww + 10) * s2, 7); }
    ctx.restore();
  });
  ctx.restore();
  stamp(t, 42.5, 'NO BREAKTHROUGH', 1440, 270, -.1, 78, false);
}

// ============ S7 quote card: Xi ============
function shotQuote(t) {
  studioBg(t);
  const z = lerp(1.0, 1.04, seg(t, 45.0, 51.5));
  ctx.save(); ctx.translate(960, 460); ctx.scale(z, z); ctx.translate(-960, -460);
  // portrait at right
  const pk = eo(seg(t, 45.0, 45.4)), px = 1350, py = 150, pw = 420, ph = 560;
  ctx.save(); ctx.globalAlpha = pk; ctx.fillStyle = 'rgba(0,0,0,.4)'; ctx.fillRect(px + 12, py + 12, pw, ph);
  photo(IM.xi, 230, 300, lerp(1.45, 1.36, seg(t, 45.0, 51.5)), px + (1 - pk) * 60, py, pw, ph);
  ctx.fillStyle = C.lemon; ctx.fillRect(px + (1 - pk) * 60, py + ph - 6, pw, 6); ctx.restore();
  const qk = seg(t, 45.1, 45.3); if (qk > 0) { const s = 1 + .6 * (1 - eo(qk)); ctx.save(); ctx.translate(200, 280); ctx.scale(s, s); ctx.globalAlpha = qk; text('“', -50, 100, F.b8(300), C.lemon); ctx.restore(); }
  pushUp(t, 46.9, 410, 100, () => text('Nuclear war cannot', 160, 410, F.b8(100), C.white, 'left', 1, 'q1'));
  pushUp(t, 47.1, 520, 100, () => text('be won and must not', 160, 520, F.b8(100), C.white, 'left', 1, 'q2'));
  pushUp(t, 47.3, 630, 100, () => text('be fought.”', 160, 630, F.b8(100), C.white, 'left', 1, 'q3'));
  // underline sweeps "must not be fought" as the voice says it
  const u = eio(seg(t, 49.2, 50.0));
  if (u > 0) {
    const x1 = 160 + tw('be won and ', F.b8(100), 1), w1 = tw('must not', F.b8(100), 1), w2 = tw('be fought.', F.b8(100), 1);
    ctx.fillStyle = C.lemon; ctx.fillRect(x1, 540, w1 * clamp(u * 2), 8); ctx.fillRect(160, 650, w2 * clamp(u * 2 - 1), 8);
  }
  const a = seg(t, 47.6, 48.0); ctx.globalAlpha = a;
  ctx.fillStyle = C.gold; ctx.fillRect(162, 690, 260 * eo(a), 3);
  text('XI JINPING', 162, 740, F.b8(40), C.lemon, 'left', 3, 'qn');
  text('SHENZHEN · 19 NOV 2026', 400, 740, F.mono(18), C.grey, 'left', 2, 'qo');
  ctx.globalAlpha = 1; ctx.restore();
}

// ============ S8 the world watches (hard cuts every bar) ============
const WORLD = [
  ['cafe', 51.5, 53.5, [1150, 520], [.80, .88]],
  ['student', 53.5, 55.5, [1650, 520], [.92, .82]],
  ['port', 55.5, 57.5, [900, 700], [.86, .86], [-90, 90]],
  ['sofa', 57.5, 60.2, [1250, 650], [.82, .92], [60, -60]],
];
function shotWorld(t) {
  let P = WORLD[0]; for (const p of WORLD) if (t >= p[1]) P = p;
  const [n, a, b, f, z, pan] = P, k = seg(t, a - .3, b);
  const fx = f[0] + (pan ? lerp(pan[0], pan[1], k) * 2 : 0);
  plateShot(IM[n], fx, f[1], lerp(z[0], z[1], k), t);
}

// ============ S10 end card ============
function shotEnd(t) {
  studioBg(t);
  const m = (a, b) => eo(seg(t, a, b));
  ctx.globalAlpha = m(67.4, 67.7); plate(960, 300, .62, seg(t, 68.0, 68.45) || -1, seg(t, 67.4, 67.9)); ctx.globalAlpha = 1;
  ctx.globalAlpha = m(67.9, 68.2); wordmark(960, 470, 52, 'e1'); ctx.globalAlpha = 1;
  pushUp(t, 68.2, 580, 80, () => text('The Shenzhen Summit', 960, 580, F.b6i(78), C.white, 'center', 1, 'e2'));
  ctx.globalAlpha = m(68.2, 68.5); text('A SPECIAL REPORT · 19 NOVEMBER 2026', 960, 630, F.mono(22), C.gold, 'center', 4, 'e3');
  ctx.fillStyle = C.line; ctx.fillRect(360, 690, 1200, 1);
  ['Reporting: Al Jazeera, Reuters, Fox News · Photos: White House (public domain), Kremlin.ru (CC BY 4.0)',
   'People in scenes marked ILLUSTRATION are AI-generated (Magnific) and fictional · Voice: Kokoro (Apache 2.0)',
   'Music samples: VSCO 2 CE, VCSL (CC0) · Fonts: Barlow Condensed, IBM Plex Mono (OFL)'].forEach((s, i) => text(s, 960, 740 + i * 34, F.b6(24), C.grey, 'center', .5, 'ec' + i, true));
  ctx.globalAlpha = 1;
}

// ============ compositing ============
function wipeBand(bx) { ctx.fillStyle = C.lemon; ctx.fillRect(bx - 84, 0, 84, H); ctx.fillStyle = C.ink; ctx.fillRect(bx, 0, 5, H); ctx.fillStyle = C.gold; ctx.fillRect(bx + 5, 0, 14, H); }
function layer(fn, t, tov) { fn(t); cornerTag(tov); source(tov); strap(tov); }
function wipe(t, a, b, oldFn, newFn) {
  const bx = lerp(-140, W + 140, eio(seg(t, a, b)));
  const n0 = TX.length; layer(newFn, t, b + .001); const NEW = TX.splice(n0);
  ctx.save(); ctx.beginPath(); ctx.rect(bx, 0, W, H); ctx.clip(); layer(oldFn, t, a - .001); ctx.restore();
  const OLD = TX.splice(n0); TX.push(...(seg(t, a, b) < .5 ? OLD : NEW));
  wipeBand(bx);
}
const STING = t => shotSting(t - 4.5), BOOK = t => shotCold(t, true), COLD = t => shotCold(t, false);
const SCENES = [[0, COLD], [4.5, STING], [6.0, shotDate], [14.5, shotWho], [21.0, shotDecl], [34.0, shotOmit], [45.0, shotQuote], [51.5, shotWorld], [60.0, BOOK], [67.5, shotEnd]];
const WIPES = [[5.7, 6.0], [14.2, 14.5], [20.7, 21.0], [33.7, 34.0], [51.2, 51.5], [59.7, 60.0]];
function scene(t) {
  const w = WIPES.find(([a, b]) => t >= a && t < b);
  if (w) { const i = SCENES.findIndex(s => Math.abs(s[0] - w[1]) < .01); wipe(t, w[0], w[1], SCENES[i - 1][1], SCENES[i][1]); }
  else if (t >= 67.25 && t < 67.5) {   // slanted wipe into the end card
    layer(BOOK, t, t);
    const k = eio(seg(t, 67.25, 67.5)); const x = W - k * (W + 340);
    ctx.save(); ctx.beginPath(); ctx.moveTo(x + 340, 0); ctx.lineTo(W + 340, 0); ctx.lineTo(W + 340, H); ctx.lineTo(x, H); ctx.closePath(); ctx.clip(); shotEnd(t); ctx.restore();
    ctx.fillStyle = C.lemon; ctx.beginPath(); ctx.moveTo(x + 340, 0); ctx.lineTo(x + 380, 0); ctx.lineTo(x + 40, H); ctx.lineTo(x, H); ctx.fill();
  } else { let fn = SCENES[0][1]; for (const [a, f] of SCENES) if (t >= a) fn = f; layer(fn, t, t); }
  if (t >= 4.5 && t < 6.0) stingLogo(t - 4.5);
}
function render(t) {
  TX = [];
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
  scene(t); bug(t);
  if (t < .5) { ctx.fillStyle = `rgba(0,0,0,${1 - seg(t, 0, .5)})`; ctx.fillRect(0, 0, W, H); }
  if (t > 71.2) { ctx.fillStyle = `rgba(0,0,0,${seg(t, 71.2, 71.9)})`; ctx.fillRect(0, 0, W, H); }
}

// —— events for mix.py ——
const EV = [
  { t: 0, type: 'rain', dur: 4.6 }, { t: 1.0, type: 'buzz' }, { t: 1.05, type: 'slide' },
  { t: 4.5, type: 'hitcut' }, { t: 4.54, type: 'swish' }, { t: 4.9, type: 'stab' }, { t: 5.4, type: 'glint' }, { t: 5.7, type: 'whoosh' },
  ...'19 NOV 2026'.split('').map((c, i) => c === ' ' ? null : { t: 6.6 + i * .06, type: 'flap' }).filter(Boolean),
  ...'SHENZHEN'.split('').map((c, i) => ({ t: 7.8 + i * .06, type: 'flap' })),
  { t: 9.3, type: 'slam' }, { t: 10.1, type: 'slam' }, { t: 10.6, type: 'slam' }, { t: 12.0, type: 'stamp' },
  { t: 14.2, type: 'whoosh' }, { t: 14.75, type: 'card' }, { t: 15.95, type: 'card' }, { t: 17.15, type: 'card' }, { t: 17.3, type: 'slide' },
  { t: 20.7, type: 'whoosh' }, { t: 21.0, type: 'paper' }, { t: 25.0, type: 'check' }, { t: 27.0, type: 'check' }, { t: 29.0, type: 'check' }, { t: 32.5, type: 'check' },
  { t: 33.7, type: 'whoosh' }, { t: 35.5, type: 'row' }, { t: 37.6, type: 'strike' }, { t: 38.4, type: 'row' }, { t: 41.0, type: 'strike' }, { t: 42.5, type: 'stamp_big' },
  { t: 45.0, type: 'hitcut' }, { t: 45.1, type: 'quote' }, { t: 49.2, type: 'mark' },
  { t: 51.2, type: 'whoosh' }, { t: 51.5, type: 'cut' }, { t: 53.5, type: 'cut' }, { t: 55.5, type: 'cut' }, { t: 57.5, type: 'cut' },
  { t: 59.7, type: 'whoosh' }, { t: 60.0, type: 'rain', dur: 7.6 }, { t: 60.1, type: 'slide' },
  { t: 67.25, type: 'whoosh' }, { t: 67.5, type: 'end' },
];
const VO_AT = { v1: .4, v2: 6.3, v3: 14.8, v4: 21.3, v5: 34.3, v6: 45.3, v7: 51.8, v8: 60.3 };
for (const id in VO_AT) EV.push({ t: VO_AT[id], type: 'vo', id });

window.DUR = DUR; window.EV = EV; window.render = render; window.TEXTS = t => { render(t); return TX; };
(async () => {
  makeGrain();
  const src = { street: 'assets/plates/street.jpg', cafe: 'assets/plates/cafe.jpg', student: 'assets/plates/student.jpg', port: 'assets/plates/port.jpg', sofa: 'assets/plates/sofa.jpg', room: 'assets/plates/room.jpg',
    trump: 'assets/photos/trump_crop.jpg', xi: 'assets/photos/xi_crop.jpg', putin: 'assets/photos/putin_crop.jpg' };
  const ks = Object.keys(src); const ims = await Promise.all(ks.map(k => loadImg(src[k]))); ks.forEach((k, i) => IM[k] = ims[i]);
  await Promise.all([F.b8(40), F.b6(40), F.b6i(40), F.mono(40)].map(f => document.fonts.load(f, 'Aa19')));
  render(0); window.READY = true;
})();
