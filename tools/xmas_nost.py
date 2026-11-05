# Nostalgic Christmas cue v2 — softer, humanized, real (convolution) reverb, no harsh transients
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve
SR = 44100; BPM = 100; beat = 60/BPM; bar = 4*beat
DUR = 17.0; N = int(SR*DUR); t = np.arange(N)/SR
rng = np.random.default_rng(5)
def hz(m): return 440*2**((m-69)/12)
def lp(x, fc, o=2): b, a = butter(o, fc/(SR/2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc/(SR/2), 'high'); return lfilter(b, a, x)
L = np.zeros(N); R = np.zeros(N)
def add(sig, start, pan=0.5, g=1.0):
    s0 = int(max(0, start)*SR)
    if s0 >= N: return
    n = min(len(sig), N-s0)
    L[s0:s0+n] += sig[:n]*g*np.cos(pan*np.pi/2); R[s0:s0+n] += sig[:n]*g*np.sin(pan*np.pi/2)
def env_adsr(n, a, d_rate):
    tt = np.arange(n)/SR
    return np.minimum(1, tt/a)*np.exp(-tt*d_rate)
def hum(): return rng.normal(0, 0.008)          # timing humanize (s)
def vel(): return 1 + rng.normal(0, 0.08)       # velocity humanize

chords = [[50, 62, 66, 69], [47, 62, 66, 71], [43, 62, 67, 71], [43, 62, 67, 70], [45, 62, 66, 69], [45, 61, 64, 67], [38, 62, 66, 69]]

# --- celesta / music box: bell partials, soft attack, slight chorus
def celesta(f, dur, v):
    n = int(dur*SR); tt = np.arange(n)/SR; s = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 1.6), (2, 0.18, 3.0), (3.01, 0.12, 5.0), (4.2, 0.05, 8.0)):
        for det in (-0.6, 0.6):
            s += amp*np.sin(2*np.pi*(f*ratio + det)*tt + rng.random()*6)*np.exp(-tt*dec)
    return lp(s*np.minimum(1, tt/0.006)*0.5, 7000)*v
mel = [(0, 0, 78, 1), (0, 1, 81, 1), (0, 2, 83, 1.5), (0, 3.5, 81, .5),
       (1, 0, 78, 1), (1, 1, 74, 1), (1, 2, 76, 1), (1, 3, 78, 1),
       (2, 0, 79, 1), (2, 1, 83, 1), (2, 2, 81, 1.5), (2, 3.5, 79, .5),
       (3, 0, 82, 1.5), (3, 1.5, 81, .5), (3, 2, 79, 2),
       (4, 0, 78, 1), (4, 1, 76, 1), (4, 2, 74, 1), (4, 3, 78, 1),
       (5, 0, 76, 1), (5, 1, 73, 1), (5, 2, 76, 1), (5, 3, 81, 1),
       (6, 0, 86, 4)]
for b_, bt, m, ln in mel:
    st = b_*bar + bt*beat + hum()
    # slight ritardando in the last bar
    accent = 1.08 if bt == 0 else 0.92
    add(celesta(hz(m), max(1.6, ln*beat+1.2), 0.11*vel()*accent), st, pan=0.42)

# --- harp-like broken chords (softer than pizzicato)
def harp(f, v):
    n = int(1.4*SR); tt = np.arange(n)/SR
    s = sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(2.5+2.5*k))/(k**1.3) for k in range(1, 5))
    return lp(s*np.minimum(1, tt/0.004), 3000)*v
for i, ch in enumerate(chords):
    pattern = [ch[0]+12, ch[1], ch[2], ch[3], ch[2], ch[1], ch[2], ch[3]] if i < 6 else [ch[0]+12, ch[1], ch[2], ch[3]]
    for k, m in enumerate(pattern):
        step = beat/2 if i < 6 else beat/3
        add(harp(hz(m-12), 0.05*vel()), i*bar + k*step + hum(), pan=0.62)
    # bass: soft bowed tone, swells instead of thumps
    n = int(bar*(2.5 if i == 6 else 1.05)*SR); tt = np.arange(n)/SR
    f = hz(ch[0]-12+12)
    b = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt))*np.minimum(1, tt/0.25)*np.minimum(1, (n/SR-tt)/0.3)
    add(lp(b, 600)*0.07, i*bar, pan=0.5)

# --- string section: many detuned voices with vibrato, slow swell, dark filter
pad = np.zeros(N)
for i, ch in enumerate(chords):
    s0 = int(i*bar*SR); n = min(int(bar*(2.6 if i == 6 else 1.08)*SR), N-s0); tt = np.arange(n)/SR
    sig = np.zeros(n)
    for m in ch[1:]:
        for v_ in range(4):
            f = hz(m)*(1 + rng.normal(0, 0.0025))
            vib = 0.004*np.sin(2*np.pi*(5 + rng.random())*tt + rng.random()*6)
            ph = np.cumsum(f*(1+vib))/SR
            sig += np.sin(2*np.pi*ph) + 0.35*np.sin(4*np.pi*ph) + 0.15*np.sin(6*np.pi*ph)
    e = np.minimum(1, tt/0.7)*np.minimum(1, (n/SR-tt)/0.5)
    pad[s0:s0+n] += sig*e
pad = lp(pad, 2200, 2)*0.010*np.clip(0.3 + t/4, 0, 1)
L += pad*0.95; R += pad*1.05

# --- sleigh bells: clusters of tiny metallic tinks, soft, dynamic, from bar 2 to bar 6
def jingle(v):
    n = int(0.25*SR); s = np.zeros(n); tt = np.arange(n)/SR
    for _ in range(9):
        off = int(abs(rng.normal(0, 0.012))*SR); f = rng.uniform(3500, 7500)
        seg = tt[:n-off]
        s[off:] += np.sin(2*np.pi*f*seg + rng.random()*6)*np.exp(-seg*rng.uniform(25, 45))*np.minimum(1, seg/0.002)
    return lp(s, 9000)*v/9
for k in range(int(5*bar/(beat/2))):
    st = bar + k*beat/2
    if st > 6*bar: break
    g = 0.06 if k % 2 else 0.035
    g *= np.clip((st-bar)/bar, 0.3, 1)         # fade in
    add(jingle(g*vel()), st + hum(), pan=0.72)

# --- end sparkle
for j, m in enumerate([86, 90, 93, 98]):
    add(celesta(hz(m), 2.8, 0.045), 6*bar + 1.0 + j*0.14 + hum(), pan=0.3 + 0.12*j)

# --- convolution reverb (synthetic hall IR, 2.2 s, darker tail)
irn = int(2.2*SR); ti = np.arange(irn)/SR
def ir():
    x = rng.normal(0, 1, irn)*np.exp(-ti*3.0)
    x = lp(x, 5000)*0.6 + lp(x, 1800)*0.4
    x[:int(0.012*SR)] = 0
    return x/np.sqrt((x**2).sum())
wetL = fftconvolve(L, ir())[:N]; wetR = fftconvolve(R, ir())[:N]
L = L*0.78 + wetL*0.42; R = R*0.78 + wetR*0.42
# gentle warmth: tiny high shelf cut and low cut
L = hp(lp(L, 11000), 45); R = hp(lp(R, 11000), 45)
fade = np.minimum(1, t/0.25)*np.minimum(1, (DUR-t)/1.8)
st = np.stack([L, R], 1)*fade[:, None]
st = st/np.abs(st).max()*0.89      # clean normalize, no saturation
wavfile.write('/tmp/claude-0/-home-claude/df77763c-98f1-5abe-be30-12ac4f1d7d46/scratchpad/xmas/xmas_nost2.wav', SR, (st*32767).astype(np.int16))
print('ok')
