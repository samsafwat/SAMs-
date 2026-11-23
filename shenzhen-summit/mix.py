"""The Shenzhen Summit · score + foley + voice → out/mix.wav (48 kHz stereo; mux brings it to −14 LUFS)
120 BPM, beat 0 = 6.0 s. Cold open: rain + drone. Sting tutti at 4.9. Theme 6–21, policy mood 21–34, tense 34–41.9,
one beat of silence 41.9–42.5, NO BREAKTHROUGH hit 42.5 + held drone, quote: pads only, the world: G-major lift,
bookend: rain returns, resolve, E-major tutti on the end card.
Run: $LIB/.venv/bin/python mix.py"""
import json, os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB', '/root/lemo-opuscar')
sys.path.insert(0, os.path.join(LIB, 'core/audio'))
import sfx as X
import sampler as S

SR = X.SR
EVD = json.load(open(os.path.join(HERE, 'events.json')))
DUR, EV = EVD['dur'], EVD['ev']
N = int(DUR * SR) + SR
music = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); vo = np.zeros((N, 2), np.float32); amb = np.zeros((N, 2), np.float32)
tt = np.arange(N) / SR
B, T0 = .5, 6.0
def bt(k): return T0 + k * B
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
CH = ['Em', 'C', 'G', 'D',  'Em', 'C', 'Am', 'B',          # 6–22 theme
      'Em', 'C', 'Am', 'B', 'Em', 'C',                    # 22–34 declaration (policy)
      'Am', 'B', 'Em', 'B',                               # 34–42 omissions (tense)
      'Em',                                               # 42–44 silence → stamp → drone
      'Em', 'C', 'G', 'D',                                # 44–52 quote (pads)
      'G', 'D', 'Em', 'C',                                # 52–60 the world (lift)
      'G', 'D', 'C', 'D',                                 # 60–68 bookend (resolve)
      'E', 'E']                                           # 68–72 end card
def triad(ch, o):
    r = 12 * (o + 1) + NOTE[ch.rstrip('m')]; return [r, r + (3 if ch.endswith('m') else 4), r + 7]
def state(t):
    if t < 6.0: return 'off'
    if t < 21.0: return 'full'
    if t < 34.0: return 'sparse'
    if t < 41.9: return 'tense'
    if t < 45.0: return 'off'
    if t < 51.5: return 'pad'
    if t < 60.0: return 'lift'
    if t < 67.5: return 'resolve'
    return 'off'

M = []
def ev(t, inst, pitch, dur, vel, pan=0, gain=1.0, **kw): M.append(dict(t=t, inst=inst, pitch=pitch, dur=dur, vel=vel, pan=pan, gain=gain, **kw))
stab = lambda t, notes, v=.9, d=.35: [ev(t, ins, n + o, d, v, pan, g) for ins, o, pan, g in [('trumpet_stac', 12, .15, .9), ('horn_stac', 0, -.2, 1.0), ('trombone_stac', -12, .05, 1.0)] for n in notes]

# cold open: low E drone under the rain (cellos + contrabass, very soft)
ev(0.2, 'cellos', 40, 4.4, .25, -.1, .45, attack=1.2, release=.5); ev(0.2, 'contrabass', 28, 4.4, .25, .1, .4, attack=1.2, release=.5)
# sting (local times + 4.5)
S0 = 4.5
for i, p in enumerate([64, 67, 71, 76]): ev(S0 + i * .02, 'violins_trem', p, .42, .25 + i * .05, (i - 1.5) * .2, .5, attack=.35)
stab(S0 + .4, [64, 67, 71], .95, .5)
ev(S0 + .4, 'timpani', 'E3', 1, .95, 0, 1.3); ev(S0 + .4, 'bass_drum', None, None, .9, 0, 1.1); ev(S0 + .4, 'crash', None, None, .7, .1, .7)
for i, p in enumerate([76, 83, 79, 88]): ev(S0 + .82 + i * .1, 'glockenspiel', p, .6, .55, .3 - i * .2, .7)

END = 67.45
for bar, ch in enumerate(CH):
    tb = bt(bar * 4)
    if tb >= END: break
    tri = triad(ch, 3); pat = [tri[0] + 12, tri[2] + 12, tri[0] + 24, tri[2] + 12]
    st0 = state(tb + .1)
    for k in range(8):   # spiccato violins
        t = tb + k * B / 2; st = state(t)
        if st in ('off', 'pad', 'resolve') or t >= END: continue
        if st == 'sparse' and k % 2: continue
        v = (.42 if k % 2 == 0 else .32) * (.8 if st == 'sparse' else 1)
        ev(t, 'violins_spic', pat[k % 4] - (12 if st == 'tense' else 0), .2, v, .25, .55)
    for k in range(4):   # pizzicato bass
        t = tb + k * B; st = state(t)
        if st in ('off', 'pad') or t >= END: continue
        if st == 'resolve' and k % 2: continue
        ev(t, 'contrabass_pizz', tri[0] - 12, .4, .72 if k == 0 else .5, -.1, .9)
        if st == 'sparse' and k in (0, 2): ev(t, 'cellos_pizz', tri[1], .4, .45, .2, .5)
    if st0 in ('full', 'sparse', 'pad', 'lift', 'resolve'):
        g = .6 if st0 == 'pad' else .5
        ev(tb, 'horn', tri[1], 2.0, .3, -.25, g, attack=.25); ev(tb, 'horn', tri[2], 2.0, .28, .25, g * .9, attack=.25)
    if st0 == 'pad':
        ev(tb, 'cellos', tri[0] - 12, 2.0, .32, -.1, .5, attack=.4, release=.4); ev(tb, 'violins', tri[2] + 12, 2.0, .22, .2, .35, attack=.6, release=.5)
    if st0 == 'tense':
        ev(tb, 'violins_trem', tri[0] + 12, 2.0, .3, -.2, .45, attack=.2); ev(tb, 'violins_trem', tri[2] + 12, 2.0, .28, .2, .4, attack=.2)
    if st0 == 'lift':
        for i, n in enumerate([tri[0] + 24, tri[1] + 24, tri[2] + 24]): ev(tb + i * .25, 'glockenspiel', n, .5, .3, -.2 + i * .2, .35)
    for k in range(4):   # drums
        t = tb + k * B; st = state(t)
        if st in ('off', 'pad', 'resolve') or t >= END: continue
        if st == 'tense': ev(t, 'bass_drum', None, None, .5, 0, .7)
        elif st == 'sparse':
            if k == 0: ev(t, 'bass_drum', None, None, .4, 0, .55)
        else:
            if k in (0, 2): ev(t, 'bass_drum', None, None, .55, 0, .7)
            if k in (1, 3): ev(t, 'snare2', None, None, .35, .1, .35)

# hits
for t in (14.5, 21.0, 34.0, 45.0, 51.5, 60.0): ev(t, 'timpani', 'E3', 1, .7, 0, .9)
stab(6.0, [64, 67, 71], .75, .3)
for t, n in ((14.75, 76), (15.95, 79), (17.15, 83)): ev(t, 'glockenspiel', n, .5, .5, .2, .55); ev(t, 'timpani', 'B2', .6, .5, 0, .6)
for t, n in ((25.0, 79), (27.0, 83), (29.0, 86), (32.5, 88)): ev(t, 'glockenspiel', n, .5, .45, .25, .5)
# the stamp after one beat of silence: the heaviest hit, then a held drone
stab(42.5, [52, 55, 59], 1.0, .7); ev(42.5, 'timpani', 'E2', 1.2, 1.0, 0, 1.4); ev(42.5, 'crash', None, None, .8, -.1, .8); ev(42.5, 'bass_drum', None, None, 1.0, 0, 1.2)
ev(42.6, 'cellos', 40, 2.4, .4, -.1, .55, attack=.3, release=.4); ev(42.6, 'contrabass', 28, 2.4, .4, .1, .5, attack=.3, release=.4); ev(42.6, 'tubular_bells', 'E4', 2, .45, .2, .35)
# the world: G-major entry
stab(51.5, [67, 71, 74], .75, .35)
for t in (53.5, 55.5, 57.5): ev(t, 'timpani', 'G2', .6, .45, 0, .55)
# end card: roll → E-major tutti
for i in range(10): ev(67.0 + i * .05, 'timpani', 'B2', .3, .35 + i * .05, 0, .6)
for ins, ns, g in [('trumpet', [76, 80, 83], .7), ('horn', [64, 68, 71], .8), ('trombone', [52, 59], .8), ('violins', [76, 80, 83, 88], .5), ('cellos', [40, 52], .7)]:
    for n in ns: ev(67.5, ins, n, 3.0, .75, 0, g, attack=.02, release=1.2)
ev(67.5, 'timpani', 'E3', 1, 1.0, 0, 1.3); ev(67.5, 'crash', None, None, .8, 0, .8); ev(67.5, 'tubular_bells', 'E5', 3, .7, .2, .6); ev(67.5, 'bass_drum', None, None, 1.0, 0, 1.1)
for i, p in enumerate([76, 80, 83, 88]): ev(67.85 + i * .09, 'glockenspiel', p, .8, .5, -.3 + i * .2, .55)

music += S.render(M, DUR + 1, master=False)[:N]

def saw(f, d): t = X.t_(d); return 2 * ((t * f) % 1) - 1
pulse = np.zeros((N, 2), np.float32)
for bar, ch in enumerate(CH):
    f = 440 * 2 ** ((12 * 3 + NOTE[ch.rstrip('m')] - 69) / 12)
    for k in range(16):
        t = bt(bar * 4) + k * B / 4; st = state(t)
        if st not in ('full', 'tense', 'lift') or t >= END: continue
        x = X.lp(saw(f, .11) * X.env_exp(.11, .045), 1100 if st == 'tense' else 900)
        X.add(pulse, x.astype(np.float32), t, .15 * (1.0 if k % 4 else .6))
music += pulse
music = S.room(music, .35, .14)

# —— ambience ——
def bed(a, d, x, g):
    n0 = int(a * SR); n1 = min(N, n0 + len(x)); seg = x[:n1 - n0] * g; L = len(seg)
    fade = np.minimum(1, np.minimum(np.arange(L) / (.4 * SR), (L - np.arange(L)) / (.6 * SR)))
    amb[n0:n1] += (seg * fade)[:, None]
def rain(d):
    a, b2 = X.bp(X.noise(d), 600, 9000), X.lp(X.brown(d), 300); n = min(len(a), len(b2)); r = a[:n] * .5 + b2[:n] * .6
    rng = np.random.default_rng(3); drops = np.zeros(int(d * SR))
    for _ in range(int(d * 40)):
        c = X.bp(X.click(1.5 + rng.random(), .3), 2000, 8000); s = int(rng.random() * (len(drops) - len(c) - 1)); drops[s:s + len(c)] += c * rng.random() * .5
    n = min(len(r), len(drops)); return X.norm(r[:n] + drops[:n], .6)
def traffic(d):
    a, b2 = X.lp(X.brown(d), 180), X.bp(X.noise(d), 200, 800); n = min(len(a), len(b2)); return X.norm(a[:n] + b2[:n] * .3, .5)
cafe_bed = lambda d: X.norm(X.bp(X.noise(d), 300, 3000) * (1 + .3 * np.sin(2 * np.pi * 1.7 * X.t_(d))), .4)
for e in EV:
    if e['type'] == 'rain':
        d = e['dur']; bed(e['t'], d, rain(d), .16); bed(e['t'], d, traffic(d), .1)
bed(51.0, 2.6, cafe_bed(2.6), .07)                       # J-cut: café murmur under the wipe into the world
bed(55.5, 2.0, X.norm(X.lp(X.brown(2.0), 250), .5), .1)  # port: low wind
bed(21.0, 13.0, X.norm(X.lp(X.brown(13.0), 160), .5), .05)   # room tone under the declaration

# —— foley ——
for e in EV:
    t, ty = e['t'], e['type']
    if ty == 'swish': X.add(fx, X.whoosh(.32, .7), t, .6, -.4)
    elif ty == 'whoosh': X.add(fx, X.whoosh(.38, .8), t - .1, .55, .3)
    elif ty == 'glint': X.add(fx, X.ding(.4), t, .25, .4)
    elif ty == 'hitcut': X.add(fx, X.thump(.9, 60), t, .6)
    elif ty == 'stab': pass
    elif ty == 'buzz':
        x = (np.sign(np.sin(2 * np.pi * 170 * X.t_(.5))) * .3 * (np.sin(2 * np.pi * 12 * X.t_(.5)) > 0)).astype(np.float32); X.add(fx, X.lp(x, 900).astype(np.float32), t, .25, -.2)
        X.add(fx, X.lp(x, 900).astype(np.float32), t + .7, .2, -.2)
    elif ty == 'slide': X.add(fx, X.whoosh(.2, .5), t, .3, -.3)
    elif ty == 'flap':
        for i in range(3): X.add(fx, X.click(1.1 + i * .15, .7), t + i * .05, .25, .2)
    elif ty == 'slam': X.add(fx, X.thump(.7, 80), t, .45); X.add(fx, X.whoosh(.16, .5), t - .08, .3, .4)
    elif ty == 'stamp': X.add(fx, X.thump(.9, 90), t, .6); X.add(fx, X.clack(.7, .8), t, .4)
    elif ty == 'stamp_big': X.add(fx, X.thump(1.0, 62), t, .7); X.add(fx, X.lp(X.clack(.6, 1.0), 2500), t, .35)
    elif ty == 'card': X.add(fx, X.thump(.7, 65), t, .5); X.add(fx, X.whoosh(.2, .5), t - .08, .3)
    elif ty == 'paper': X.add(fx, (X.bp(X.noise(.45), 1200, 6000) * X.env_exp(.45, .14)).astype(np.float32), t, .3, .4); X.add(fx, X.whoosh(.35, .6), t, .35, .4)
    elif ty == 'check': X.add(fx, X.click(1.2, .8), t, .35, .3)
    elif ty == 'row': X.add(fx, X.click(.8, .9), t, .4, .3); X.add(fx, X.thump(.5, 110), t, .35)
    elif ty == 'strike': X.add(fx, (X.bp(X.noise(.45), 1500, 6000) * np.sin(np.pi * X.t_(.45) / .45)).astype(np.float32), t, .22, .3)
    elif ty == 'quote': X.add(fx, X.thump(.6, 95), t, .4); X.add(fx, X.whoosh(.25, .5), t - .05, .25, -.2)
    elif ty == 'mark': X.add(fx, (X.bp(X.noise(.8), 2500, 7000) * np.sin(np.pi * X.t_(.8) / .8)).astype(np.float32), t, .1, .3)
    elif ty == 'cut': X.add(fx, X.thump(.5, 70), t, .3)
    elif ty == 'end': X.add(fx, X.whoosh(.3, .6), t - .2, .3)
fx = S.room(fx, .2, .08)

# —— narration ——
spans = []
for e in EV:
    if e['type'] != 'vo': continue
    sr, x = wavfile.read(os.path.join(HERE, 'vo', e['id'] + '.wav'))
    x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
    if x.ndim > 1: x = x.mean(1)
    x = resample_poly(x, SR, sr).astype(np.float32)
    x = X.hp(x, 90).astype(np.float32); x = X.compress(x / (np.abs(x).max() + 1e-9) * .8, .3, 3)
    X.add(vo, x.astype(np.float32), e['t'], 1.0, 0); spans.append((e['t'], e['t'] + len(x) / SR))
duck = np.ones(N, np.float32)
for a, b in spans:
    k = np.clip(np.minimum((tt - (a - .08)) / .08, ((b + .15) - tt) / .15), 0, 1); duck = np.minimum(duck, 1 - .55 * k)
music *= duck[:, None]; amb *= (.6 + .4 * duck)[:, None]
cut = 1 - duck
band = np.stack([X.bp(music[:, c], 1200, 5000) for c in range(2)], 1).astype(np.float32)
music -= band * (cut / .55 * .6)[:, None]
# the beat of silence before the stamp: everything but the voice out
sil = np.ones(N, np.float32); m = (tt >= 41.95) & (tt < 42.48); sil[m] = 0
music *= sil[:, None]; amb *= sil[:, None]

mix = music * .9 + fx * .8 + amb * .9 + vo * 1.3
fade = np.clip((DUR - tt) / 1.0, 0, 1); mix *= fade[:, None]
mix = mix[:int(DUR * SR)]
mix = np.stack([X.limit(mix[:, 0], .95), X.limit(mix[:, 1], .95)], 1)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
wavfile.write(os.path.join(HERE, 'out', 'mix.wav'), SR, (mix * 32767).astype(np.int16))
print('mix', mix.shape, 'peak', float(np.abs(mix).max()))
open(os.path.join(HERE, 'out', 'instruments.txt'), 'w').write('\n'.join(S.credits(sorted({e['inst'] for e in M}))))
