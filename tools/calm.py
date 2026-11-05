# Calm lo-fi track, 16 s: soft Rhodes-like chords, warm pad, gentle kick/hat, light vinyl
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR = 44100; DUR = 16.0; N = int(SR*DUR)
t = np.arange(N)/SR
rng = np.random.default_rng(3)
BPM = 78; beat = 60/BPM; bar = beat*4
def hz(m): return 440*2**((m-69)/12)
def lp(x, fc, o=2): b, a = butter(o, fc/(SR/2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc/(SR/2), 'high'); return lfilter(b, a, x)
L = np.zeros(N); R = np.zeros(N)
# Fmaj9 - Em7 - Dm9 - Cmaj7 (bars)
prog = [[53, 60, 64, 67, 69], [52, 59, 62, 67], [50, 57, 60, 64, 65], [48, 55, 59, 64, 67]]
def rhodes(f, n, vel):
    tt = np.arange(n)/SR
    env = np.exp(-tt*1.6)*(1-np.exp(-tt*200))
    trem = 1 + 0.12*np.sin(2*np.pi*4.2*tt)
    s = np.sin(2*np.pi*f*tt + 0.6*np.exp(-tt*6)*np.sin(2*np.pi*f*tt)) + 0.25*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*4)
    return s*env*trem*vel
for b in range(5):
    t0 = b*bar
    if t0 >= DUR: break
    ch = prog[b % 4]
    for k, m in enumerate(ch):
        for hit, vel in ((0, 0.11), (2.5*beat, 0.06)):
            s0 = int((t0+hit+k*0.018)*SR); n = int(min(bar*1.3, DUR-t0-hit)*SR)
            if n <= 0 or s0 >= N: continue
            n = min(n, N-s0); sig = rhodes(hz(m), n, vel)
            pan = 0.5 + (k-2)*0.12
            L[s0:s0+n] += sig*(1-pan); R[s0:s0+n] += sig*pan
    # pad
    s0 = int(t0*SR); n = min(int(bar*SR), N-s0); tt = np.arange(n)/SR
    pad = sum(np.sin(2*np.pi*hz(m+12)*tt*(1+d)) for m in ch[1:3] for d in (-0.002, 0.002))
    env = np.minimum(1, tt/0.8)*np.minimum(1, (bar-tt)/0.6)
    L[s0:s0+n] += 0.018*pad*env; R[s0:s0+n] += 0.018*pad*env
    # bass
    tt = np.arange(n)/SR; bs = np.sin(2*np.pi*hz(ch[0]-12)*tt)*np.exp(-tt*0.9)*0.16
    L[s0:s0+n] += bs; R[s0:s0+n] += bs
# simple melody (pentatonic, sparse)
mel = [(1.0, 76), (1.5, 74), (2.0, 72), (3.5, 69), (5.0, 74), (5.5, 72), (6.0, 71), (7.0, 67),
       (9.0, 72), (9.5, 74), (10.0, 76), (11.5, 72), (13.0, 71), (13.5, 72), (14.0, 67)]
for bt, m in mel:
    s0 = int(bt*beat*SR*1.0)
    if s0 >= N: continue
    n = min(int(1.6*SR), N-s0); tt = np.arange(n)/SR
    sig = (np.sin(2*np.pi*hz(m)*tt) + 0.3*np.sin(2*np.pi*hz(m)*3*tt)*np.exp(-tt*8))*np.exp(-tt*2.2)*(1-np.exp(-tt*300))*0.07
    L[s0:s0+n] += sig*0.6; R[s0:s0+n] += sig*0.4
# drums (soft) from bar 1
k_t = np.arange(int(0.35*SR))/SR
kick = np.sin(2*np.pi*(45+60*np.exp(-k_t*30))*k_t)*np.exp(-k_t*9)*0.32
nb = int(DUR/beat)
for i in range(nb):
    tb = i*beat
    if tb < bar*0.99: continue
    if i % 4 in (0,) or (i % 8 == 6):
        s0 = int(tb*SR); n = min(len(kick), N-s0); L[s0:s0+n] += kick[:n]; R[s0:s0+n] += kick[:n]
    if i % 4 in (1, 3):  # soft rim/snare
        s0 = int(tb*SR); n = min(int(0.18*SR), N-s0); tt = np.arange(n)/SR
        sn = hp(rng.normal(0, 1, n), 1500)*np.exp(-tt*28)*0.05
        L[s0:s0+n] += sn; R[s0:s0+n] += sn
    for off in (0, beat/2):
        s0 = int((tb+off+0.012*(off > 0))*SR); n = min(int(0.05*SR), N-s0)
        if n <= 0: continue
        tt = np.arange(n)/SR; hh = hp(rng.normal(0, 1, n), 7000)*np.exp(-tt*90)*(0.025 if off else 0.018)
        L[s0:s0+n] += hh*0.8; R[s0:s0+n] += hh
# vinyl
vin = lp(rng.normal(0, 1, N), 3000)*0.004
cr = (rng.random(N) < 0.0004)*rng.normal(0, 0.15, N)
L += vin + lp(cr, 4000); R += vin + lp(cr, 4000)
# warmth + simple reverb
def verb(x):
    y = x.copy()
    for d, g in ((0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.167, 0.15)):
        s = int(d*SR); y[s:] += g*x[:-s]
    return y
L = lp(verb(L), 9000); R = lp(verb(R), 9000)
fade = np.minimum(1, t/0.6)*np.minimum(1, (DUR-t)/1.6)
st = np.stack([L*fade, R*fade], 1)
st = np.tanh(st/np.abs(st).max()*1.1)*0.85
wavfile.write('/tmp/claude-0/-home-claude/df77763c-98f1-5abe-be30-12ac4f1d7d46/scratchpad/cal/calm.wav', SR, (st*32767).astype(np.int16))
print('ok')
