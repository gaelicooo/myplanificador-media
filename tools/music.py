import numpy as np, wave
SR=44100; rng=np.random.default_rng(1)
N={}
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
for o in range(1,7):
    for i,n in enumerate(names): N[f'{n}{o}']=440*2**((i-9)/12+(o-4))
def tone(f,d,kind='bell'):
    t=np.arange(int(SR*d))/SR
    if kind=='bell':
        s=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)+0.25*np.sin(2*np.pi*4.01*f*t); env=np.exp(-5*t)
    elif kind=='lead':
        s=np.sign(np.sin(2*np.pi*f*t))*0.35+np.sin(2*np.pi*f*t)*0.65; env=np.minimum(1,t*60)*np.exp(-2.5*t)
    elif kind=='bass':
        s=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t); env=np.minimum(1,t*80)*np.exp(-4*t)
    elif kind=='pad':
        s=sum(np.sin(2*np.pi*f*m*t) for m in (1,1.005,2.0))/3; env=np.minimum(1,t*8)*np.exp(-1.2*t)
    return s*env
def kick():
    t=np.arange(int(SR*.25))/SR; f=110*np.exp(-18*t)+45; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-9*t)
def snare():
    t=np.arange(int(SR*.18))/SR; return rng.normal(0,1,len(t))*np.exp(-22*t)*0.6+np.sin(2*np.pi*190*t)*np.exp(-30*t)*0.4
def hat():
    t=np.arange(int(SR*.05))/SR; n=rng.normal(0,1,len(t)); n=np.diff(n,prepend=0); return n*np.exp(-80*t)*0.35
def add(buf,s,t,g):
    i=int(t*SR); j=min(len(buf),i+len(s)); buf[i:j]+=s[:j-i]*g
def song(melody,chords,bpm,total,lead='bell'):
    beat=60/bpm; L=int(SR*(total+2)); mel=np.zeros(L); bas=np.zeros(L); drm=np.zeros(L); pad=np.zeros(L)
    t=0
    while t<total:
        for n,b in melody:
            if t>=total: break
            if n: add(mel,tone(N[n],max(b*beat,.25),lead),t,.5)
            t+=b*beat
    t=0; ci=0
    while t<total:
        root,ch=chords[ci%len(chords)]
        for k in range(4):
            add(bas,tone(N[root]*(1 if k%2==0 else 2),beat*.9,'bass'),t+k*beat,.55)
        for n in ch: add(pad,tone(N[n],beat*4,'pad'),t,.12)
        for k in range(4):
            add(drm,kick(),t+k*beat,.9 if k in (0,2) else 0)
            if k in (1,3): add(drm,snare(),t+k*beat,.5)
            add(drm,hat(),t+k*beat+beat/2,1); add(drm,hat(),t+k*beat,.6)
        t+=4*beat; ci+=1
    mix=mel+bas+drm+pad; mix=mix[:int(SR*total)]
    fi=int(SR*.05); mix[:fi]*=np.linspace(0,1,fi); fo=int(SR*1.0); mix[-fo:]*=np.linspace(1,0,fo)
    mix=np.tanh(mix*1.3); return mix/np.max(np.abs(mix))*0.85
def save(fn,x):
    y=(x*32767).astype(np.int16); y=np.stack([y,y],1)
    with wave.open(fn,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
# Jingle Bells (1857, dominio público) en clave de Sol, alegre
jb=[('E5',1),('E5',1),('E5',2),('E5',1),('E5',1),('E5',2),('E5',1),('G5',1),('C5',1.5),('D5',.5),('E5',4),
    ('F5',1),('F5',1),('F5',1.5),('F5',.5),('F5',1),('E5',1),('E5',1),('E5',.5),('E5',.5),('E5',1),('D5',1),('D5',1),('E5',1),('D5',2),('G5',2)]
chords_x=[('C2',['C4','E4','G4']),('C2',['C4','E4','G4']),('F2',['F4','A4','C5']),('C2',['C4','E4','G4']),('F2',['F4','A4','C5']),('C2',['C4','E4','G4']),('D2',['D4','F#4','A4']),('G2',['G4','B4','D5'])]
save('xmas2.wav',song(jb,chords_x,150,15,'bell'))
# pop alegre original
pm=[('E5',.5),('G5',.5),('A5',1),('G5',.5),('E5',.5),('D5',1),('C5',.5),('D5',.5),('E5',1),('G5',1),('A5',.5),('G5',.5),('E5',1),('D5',2)]
chords_p=[('C2',['C4','E4','G4']),('G2',['G4','B4','D5']),('A2',['A4','C5','E5']),('F2',['F4','A4','C5'])]
save('pop2.wav',song(pm,chords_p,124,15,'lead'))
