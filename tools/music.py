import numpy as np, wave
SR=44100
def note(f,d,vol=0.35):
    t=np.arange(int(SR*d))/SR
    env=np.exp(-3.2*t)
    s=(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)+0.12*np.sin(2*np.pi*3*f*t))*env
    a=int(0.005*SR); s[:a]*=np.linspace(0,1,a)
    return s*vol
N={'C4':261.63,'D4':293.66,'E4':329.63,'F4':349.23,'G4':392.0,'A4':440.0,'B4':493.88,'C5':523.25,'D5':587.33,'E5':659.25,'F5':698.46,'G5':783.99}
def render(seq,bpm,total,bass=None):
    beat=60/bpm; out=np.zeros(int(SR*total)+SR*3); t=0.0
    while t<total:
        for n,b in seq:
            if n: 
                s=note(N[n],max(b*beat,0.6)); i=int(t*SR); out[i:i+len(s)]+=s[:len(out)-i]
            t+=b*beat
            if t>=total: break
    out=out[:int(SR*total)]
    fade=int(SR*1.2); out[-fade:]*=np.linspace(1,0,fade)
    return out/np.max(np.abs(out))*0.6
def save(fn,x):
    y=(x*32767).astype(np.int16); y=np.stack([y,y],1)
    with wave.open(fn,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
# Jingle Bells (James Lord Pierpont, 1857 - dominio público), en caja de música
jb=[('E5',1),('E5',1),('E5',2),('E5',1),('E5',1),('E5',2),('E5',1),('G5',1),('C5',1.5),('D5',.5),('E5',4),
    ('F5',1),('F5',1),('F5',1.5),('F5',.5),('F5',1),('E5',1),('E5',1),('E5',.5),('E5',.5),('E5',1),('D5',1),('D5',1),('E5',1),('D5',2),('G5',2)]
save('xmas.wav',render(jb,132,16))
# arpegio tranquilo neutro
arp=[('C5',.5),('E5',.5),('G5',.5),('E5',.5)]*2+[('A4',.5),('C5',.5),('E5',.5),('C5',.5)]*2+[('F4',.5),('A4',.5),('C5',.5),('A4',.5)]*2+[('G4',.5),('B4',.5),('D5',.5),('B4',.5)]*2
save('neutral.wav',render(arp,110,16))
