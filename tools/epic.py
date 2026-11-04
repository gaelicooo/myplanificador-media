import numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve
SR=44100; DUR=15.0; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(3)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def saw(f,tt,ph=0): return 2*((f*tt+ph)%1)-1
def note(m): return 440*2**((m-69)/12)
out=np.zeros((N,2))
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    out[i:i+n,0]+=sig[:n]*g*l; out[i:i+n,1]+=sig[:n]*g*r
BEAT=60/90  # 90 bpm
# chords (minor epic): Dm  Bb  F  C  -> 2 bars each of 4 beats? use 1 bar each = 2.667 s
prog=[[50,57,62,65],[46,53,58,62],[41,48,53,57,60],[48,55,60,64]]
bar=4*BEAT
def strings(ms,dur,amp):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        f=note(m)
        for d in (-0.08,0,0.08):
            s+=saw(f*2**(d/12),tt,rng.random())
    s=0.5*lp(s,1400)+0.5*lp(s,2600)*np.sin(np.pi*np.arange(n)/n)
    env=np.minimum(1,tt/0.9)*np.minimum(1,(dur-tt)/0.6)
    return s*env*amp/len(ms)
for k in range(5):
    ch=prog[k%4]; st=k*bar
    if st>=DUR: break
    amp=0.10+0.05*k
    add(strings(ch,bar+0.35,amp),st,-0.3); add(strings([m+12 for m in ch[1:]],bar+0.35,amp*0.55),st,0.35)
# drone bass
drone=lp(saw(note(26),t)+0.6*saw(note(38),t),220)*0.22*np.minimum(1,t/2)
add(drone,0)
# taiko
def taiko(g):
    n=int(1.2*SR); tt=np.arange(n)/SR
    f=55*np.exp(-tt*6)+38
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*5.5)
    click=lp(rng.normal(0,1,n),900)*np.exp(-tt*40)*0.6
    return (body+click)*g
pattern=[]
for b in range(int(DUR/BEAT)):
    tb=b*BEAT
    if tb<2.6: 
        if b%4==0: pattern.append((tb,0.55))
    elif tb<10.5:
        pattern.append((tb,0.6 if b%2==0 else 0.35))
        if b%4==3: pattern.append((tb+BEAT/2,0.3))
    else:
        pattern += [(tb,0.75),(tb+BEAT/2,0.45)]
for tb,g in pattern:
    if tb<12.9: add(taiko(g),tb,rng.uniform(-0.2,0.2))
# snare-ish ostinato in middle
def hit(g):
    n=int(0.25*SR); tt=np.arange(n)/SR
    return bp(rng.normal(0,1,n),300,4000)*np.exp(-tt*22)*g
for b in range(int(5.3/ (BEAT/2)), int(12.8/(BEAT/2))):
    add(hit(0.12 if b%2 else 0.2),b*BEAT/2,0.25)
# brass swell (low, filtered square-ish) on last chord + rise
def brass(ms,dur,amp):
    n=int(dur*SR); tt=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        f=note(m); s+=np.sign(np.sin(2*np.pi*f*tt))*0.6+saw(f,tt)*0.4
    ramp=np.minimum(1,tt/dur*1.6)
    s=lp(s,600)*(1-ramp)+lp(s,2400)*ramp
    env=np.minimum(1,tt/0.5)*np.minimum(1,(dur-tt)/0.3)
    return s*env*amp/len(ms)
add(brass([38,45,50,53],2.6,0.22),8.0); add(brass([34,41,46,50],2.4,0.26),10.6)
# riser + cymbal swell
n=int(2.4*SR); tt=np.arange(n)/SR
riser=hp(rng.normal(0,1,n),2500)*(tt/2.4)**2*0.18
add(riser,10.5)
# final impact at 12.95
n=int(2.05*SR); tt=np.arange(n)/SR
boom=np.sin(2*np.pi*np.cumsum(70*np.exp(-tt*3)+28)/SR)*np.exp(-tt*1.6)*0.9
boom+=lp(rng.normal(0,1,n),3000)*np.exp(-tt*4)*0.35
boom+=strings([38,50,57,62,65,69],2.05,0.35)[:n]*np.exp(-tt*0.8)
add(boom,12.95)
# reverb
ir_n=int(2.2*SR); ir=rng.normal(0,1,ir_n)*np.exp(-np.arange(ir_n)/SR*2.8); ir=lp(ir,5000); ir/=np.sqrt((ir**2).sum())
wet=np.stack([fftconvolve(out[:,c],ir)[:N] for c in range(2)],1)
mix=out*0.8+wet*0.45
# master
fade=np.ones(N); fs=int(0.8*SR); fade[-fs:]=np.linspace(1,0,fs)
mix*=fade[:,None]
mix=np.tanh(mix*1.4)
mix/=np.abs(mix).max()/0.89
y=(mix*32767).astype(np.int16)
with wave.open('epic.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
print('ok')
