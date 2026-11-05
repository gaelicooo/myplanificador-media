# Original nostalgic Christmas cue, ~16 s: music box/celesta melody, pizzicato, warm strings, sleigh bells
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR = 44100; BPM = 104; beat = 60/BPM; bar = 4*beat
DUR = 16.4; N = int(SR*DUR); t = np.arange(N)/SR
rng = np.random.default_rng(11)
def hz(m): return 440*2**((m-69)/12)
def lp(x, fc, o=2): b, a = butter(o, fc/(SR/2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc/(SR/2), 'high'); return lfilter(b, a, x)
L = np.zeros(N); R = np.zeros(N)
def add(sig, start, pan=0.5, g=1.0):
    s0 = int(start*SR)
    if s0 >= N: return
    n = min(len(sig), N-s0); L[s0:s0+n] += sig[:n]*g*(1-pan)*2*0.5+0*pan; R[s0:s0+n] += sig[:n]*g*pan*2*0.5 + sig[:n]*g*0.0
D, Fs, A, B = 62, 66, 69, 71
# chords per bar: D, Bm, G, Gm (nostalgic), D/A, A7, D
chords = [[50, 62, 66, 69], [47, 62, 66, 71], [43, 62, 67, 71], [43, 62, 67, 70], [45, 62, 66, 69], [45, 61, 64, 67], [38, 62, 66, 69]]
# --- music box / celesta
def celesta(f, dur, vel):
    n = int(dur*SR); tt = np.arange(n)/SR
    s = (np.sin(2*np.pi*f*tt)*np.exp(-tt*2.2) + 0.35*np.sin(2*np.pi*f*3.0*tt)*np.exp(-tt*6)
         + 0.12*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*12) + 0.2*np.sin(2*np.pi*f*2*tt)*np.exp(-tt*4))
    return s*(1-np.exp(-tt*400))*vel
# melody (bar, beat, midi, len_beats) — original
mel = [(0, 0, 78, 1), (0, 1, 81, 1), (0, 2, 83, 1.5), (0, 3.5, 81, .5),
       (1, 0, 78, 1), (1, 1, 74, 1), (1, 2, 76, 1), (1, 3, 78, 1),
       (2, 0, 79, 1), (2, 1, 83, 1), (2, 2, 81, 1.5), (2, 3.5, 79, .5),
       (3, 0, 82, 1.5), (3, 1.5, 81, .5), (3, 2, 79, 2),
       (4, 0, 78, 1), (4, 1, 76, 1), (4, 2, 74, 1), (4, 3, 78, 1),
       (5, 0, 76, 1), (5, 1, 73, 1), (5, 2, 76, 1), (5, 3, 81, 1),
       (6, 0, 86, 4)]
for b_, bt, m, ln in mel:
    st = b_*bar + bt*beat
    sig = celesta(hz(m), max(1.4, ln*beat+1.0), 0.16)
    add(sig, st, pan=0.42)
    add(celesta(hz(m-12), max(1.2, ln*beat+0.8), 0.05), st+0.004, pan=0.6)
# --- pizzicato strings on beats (arpeggiated chord tones)
def pizz(f, vel):
    n = int(0.5*SR); tt = np.arange(n)/SR
    s = sum(np.sin(2*np.pi*f*k*tt)*np.exp(-tt*(9+5*k))/k for k in range(1, 6))
    return lp(s*(1-np.exp(-tt*600)), 2500)*vel
for i, ch in enumerate(chords):
    for bt in range(4):
        if i == 6 and bt > 0: break
        m = ch[1 + (bt % 3)] - 12
        add(pizz(hz(m), 0.09), i*bar + bt*beat, pan=0.62)
    # bass
    for bt in (0, 2):
        if i == 6 and bt: break
        n = int(beat*1.6*SR); tt = np.arange(n)/SR
        add(np.sin(2*np.pi*hz(ch[0])*tt)*np.exp(-tt*2.5)*(1-np.exp(-tt*200))*0.22, i*bar + bt*beat, pan=0.5)
# --- warm string pad (detuned saws, low-passed)
pad = np.zeros(N)
for i, ch in enumerate(chords):
    s0 = int(i*bar*SR); n = int((bar*(2.6 if i == 6 else 1.0))*SR); n = min(n, N-s0); tt = np.arange(n)/SR
    sig = np.zeros(n)
    for m in ch[1:]:
        for d in (-0.003, 0.0, 0.003):
            ph = (hz(m)*(1+d)*tt) % 1.0
            sig += (2*ph-1)
    env = np.minimum(1, tt/0.5)*np.minimum(1, (n/SR - tt)/0.4)
    pad[s0:s0+n] += sig*env
pad = lp(pad, 1400, 3)*0.012*(0.4+0.6*np.clip(t/3.0, 0, 1))
L += pad*0.9; R += pad*1.1
# --- sleigh bells on 8ths from bar 2, accent on the off-beats
for k in range(int(6*bar/(beat/2))):
    st = bar + k*beat/2
    if st > 6*bar: break
    n = int(0.12*SR); tt = np.arange(n)/SR
    jing = hp(rng.normal(0, 1, n), 6000, 3)*np.exp(-tt*35)
    jing *= (1 + 0.6*np.sin(2*np.pi*55*tt))
    add(jing*(0.05 if k % 2 else 0.032), st, pan=0.7)
# --- sparkle at the end (glock arpeggio)
for j, m in enumerate([86, 90, 93, 98]):
    add(celesta(hz(m), 2.4, 0.07), 6*bar + 0.9 + j*0.12, pan=0.3+0.1*j)
# soft room reverb
def verb(x):
    y = x.copy()
    for d, g in ((0.029, .32), (0.043, .28), (0.067, .24), (0.101, .2), (0.149, .16), (0.211, .12), (0.293, .08)):
        s = int(d*SR); y[s:] += g*x[:-s]
    return y
L = verb(L); R = verb(R[::1])
fade = np.minimum(1, t/0.3)*np.minimum(1, (DUR-t)/1.4)
st = np.stack([L, R], 1)*fade[:, None]
st = np.tanh(st/np.abs(st).max()*1.05)*0.88
wavfile.write('/tmp/claude-0/-home-claude/df77763c-98f1-5abe-be30-12ac4f1d7d46/scratchpad/xmas/xmas_nost.wav', SR, (st*32767).astype(np.int16))
print('ok', DUR)
