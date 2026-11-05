import sys, subprocess, calendar
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = '/tmp/claude-0/-home-claude/df77763c-98f1-5abe-be30-12ac4f1d7d46/scratchpad/'
F = '/usr/share/fonts/truetype/google-fonts/Poppins-'
def f(w, s): return ImageFont.truetype(F + w + '.ttf', s)
VW, VH, FPS = 1080, 1920, 30
CREAM = (237, 228, 213); INK = (30, 36, 51); TEAL = (31, 122, 107); PINK = (232, 120, 120); GOLD = (232, 176, 60)
SOFT = (110, 112, 120); WHITE = (255, 255, 255)
MES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
PROD = Image.open(S + 'cal/f5.png').convert('RGB')

def ease(u): return u*u*(3-2*u)
def pop(u, a, b):  # 0..1 appearance between a and b
    return ease(min(1, max(0, (u-a)/(b-a))))

def wrap(d, txt, fo, maxw):
    out = []
    for para in txt.split('\n'):
        cur = ''
        for w in para.split():
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=fo) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

def text(img, txt, size, y, col=INK, weight='Bold', maxw=VW-140, al=1.0):
    d = ImageDraw.Draw(img); fo = f(weight, size); lh = int(size*1.2)
    for i, l in enumerate(wrap(d, txt, fo, maxw)):
        d.text((VW/2, y + i*lh), l, font=fo, fill=col, anchor='ma')
    return y + lh*len(wrap(d, txt, fo, maxw))

def base():
    im = Image.new('RGB', (VW, VH), CREAM); d = ImageDraw.Draw(im)
    d.ellipse((VW-420, -260, VW+260, 420), fill=(243, 236, 224))
    d.text((VW/2, VH-120), 'MyPlanificador', font=f('Bold', 38), fill=INK, anchor='mm')
    return im

def month(im, y, m, marks, u, note=None):
    """marks: {day: ('fest'|'pide'|'sab', label)}; u controls reveal of marks."""
    d = ImageDraw.Draw(im)
    X0, X1 = 90, VW-90; cw = (X1-X0)/7
    d.rounded_rectangle((X0, y, X1, y+110), 26, fill=TEAL)
    d.text((X0+40, y+55), MES[m], font=f('Bold', 56), fill=WHITE, anchor='lm')
    d.text((X1-40, y+55), '2027', font=f('Medium', 44), fill=WHITE, anchor='rm')
    for i, n in enumerate(['L', 'M', 'X', 'J', 'V', 'S', 'D']):
        d.text((X0+cw*i+cw/2, y+160), n, font=f('Bold', 38), fill=SOFT if i < 5 else PINK, anchor='mm')
    weeks = calendar.Calendar(0).monthdayscalendar(2027, m)
    order = sorted(marks)
    for r, wk in enumerate(weeks):
        for c, day in enumerate(wk):
            if not day: continue
            cx = X0+cw*c+cw/2; cy = y+240+r*118
            col = INK
            if c >= 5: d.rounded_rectangle((cx-62, cy-50, cx+62, cy+50), 20, fill=(246, 240, 230))
            if day in marks:
                k = order.index(day); a = pop(u, 0.15+k*0.18, 0.3+k*0.18)
                if a > 0:
                    kind = marks[day][0]
                    fill = {'fest': PINK, 'pide': GOLD, 'sab': (150, 150, 158)}[kind]
                    rr = 56*(0.6+0.4*a)
                    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                    od.rounded_rectangle((cx-rr, cy-rr*0.9, cx+rr, cy+rr*0.9), 22, fill=fill+(int(255*a),))
                    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
                    d = ImageDraw.Draw(im); col = WHITE
            d.text((cx, cy), str(day), font=f('Bold', 46), fill=col, anchor='mm')
    yb = y+240+len(weeks)*118
    # legend for the marks present
    kinds = []
    for day in order:
        if marks[day][0] not in [k for k, _ in kinds]: kinds.append((marks[day][0], marks[day][1]))
    lx = X0
    for kind, lab in kinds:
        fill = {'fest': PINK, 'pide': GOLD, 'sab': (150, 150, 158)}[kind]
        d.rounded_rectangle((lx, yb, lx+44, yb+44), 12, fill=fill)
        d.text((lx+60, yb+22), lab, font=f('Medium', 36), fill=INK, anchor='lm')
        lx += 60 + d.textlength(lab, font=f('Medium', 36)) + 50
    return yb + 60

def badge(im, txt, y, a, fill=INK, col=WHITE, size=60):
    if a <= 0: return
    d = ImageDraw.Draw(im); fo = f('Bold', size); w = d.textlength(txt, font=fo)
    s = 0.85 + 0.15*a
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    h = size*1.9*s; W = (w+90)*s
    od.rounded_rectangle((VW/2-W/2, y, VW/2+W/2, y+h), h/2, fill=fill+(int(255*a),))
    od.text((VW/2, y+h/2), txt, font=f('Bold', int(size*s)), fill=col+(int(255*a),), anchor='mm')
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))

def hook_scene(hook, sub):
    def fn(u):
        im = PROD.copy().filter(ImageFilter.GaussianBlur(14))
        im = Image.blend(im, Image.new('RGB', (VW, VH), INK), 0.72)
        z = 1.0 + 0.05*u
        im = im.resize((int(VW*z), int(VH*z))).crop((int(VW*(z-1)/2), int(VH*(z-1)/2), int(VW*(z-1)/2)+VW, int(VH*(z-1)/2)+VH))
        y = text(im, hook, 104, VH*0.30, col=WHITE)
        a = pop(u, 0.35, 0.6)
        if a > 0: text(im, sub, 60, y+50, col=GOLD, weight='Bold')
        return im
    return fn

def cal_scene(title, m, marks, result, foot=None):
    def fn(u):
        im = base()
        y = text(im, title, 70, 170)
        yb = month(im, y+50, m, marks, u)
        badge(im, result, yb+40, pop(u, 0.62, 0.8), fill=TEAL)
        if foot: text(im, foot, 34, VH-215, col=SOFT, weight='Medium')
        return im
    return fn

def multi_scene(title, items):
    """items: list of (m, day, kind, label, line)"""
    def fn(u):
        im = base(); y = text(im, title, 70, 160)
        d = ImageDraw.Draw(im)
        for i, (lab, line) in enumerate(items):
            a = pop(u, 0.08+i*0.17, 0.22+i*0.17)
            if a <= 0: continue
            yy = y+70+i*250 + (1-a)*40
            ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle((90, yy, VW-90, yy+210), 36, fill=WHITE+(int(255*a),))
            od.rounded_rectangle((120, yy+30, 300, yy+180), 28, fill=PINK+(int(255*a),))
            dd, mm = lab.split(' ', 1)
            od.text((210, yy+88), dd, font=f('Bold', 80), fill=WHITE+(int(255*a),), anchor='mm')
            od.text((210, yy+150), mm, font=f('Bold', 32), fill=WHITE+(int(255*a),), anchor='mm')
            l1, l2 = line
            od.text((340, yy+80), l1, font=f('Bold', 50), fill=INK+(int(255*a),), anchor='lm')
            od.text((340, yy+140), l2, font=f('Medium', 38), fill=SOFT+(int(255*a),), anchor='lm')
            im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
        text(im, 'Festivos nacionales. Consulta los de tu comunidad.', 34, VH-215, col=SOFT, weight='Medium')
        return im
    return fn

def product_scene(line):
    def fn(u):
        z = 1.12 - 0.12*ease(u)
        w, h = int(VW*z), int(VH*z)
        im = PROD.resize((w, h), Image.LANCZOS).crop(((w-VW)//2, (h-VH)//2, (w-VW)//2+VW, (h-VH)//2+VH))
        badge(im, line, VH*0.80, pop(u, 0.2, 0.45), fill=TEAL, size=46)
        return im
    return fn

def endcard(u):
    im = Image.new('RGB', (VW, VH), INK); d = ImageDraw.Draw(im)
    d.text((VW/2, VH*0.36), 'MyPlanificador', font=f('Bold', 96), fill=WHITE, anchor='mm')
    d.rectangle((VW/2-90, VH*0.40, VW/2+90, VH*0.40+9), fill=TEAL)
    d.text((VW/2, VH*0.46), 'Calendario laboral 2027', font=f('Medium', 50), fill=CREAM, anchor='mm')
    d.rounded_rectangle((VW/2-330, VH*0.53, VW/2+330, VH*0.53+110), 55, fill=GOLD)
    d.text((VW/2, VH*0.53+55), '-20 % · BIENVENIDA20', font=f('Bold', 50), fill=INK, anchor='mm')
    d.text((VW/2, VH*0.65), 'Búscanos en Etsy · enlace en el perfil', font=f('Medium', 40), fill=(190, 200, 225), anchor='mm')
    return im

FOOT = 'Festivos nacionales. Consulta los de tu comunidad.'
R = {
 'puentes': [
   (3.2, hook_scene('En 2027 pierdes 2 festivos', 'Caen en sábado. Pero hay truco')),
   (3.0, cal_scene('1 de mayo y 25 de diciembre', 5, {1: ('sab', 'Festivo en sábado')}, 'Se pierden en sábado', FOOT)),
   (3.4, cal_scene('El truco de octubre', 10, {11: ('pide', 'Pide 1 día'), 12: ('fest', 'Festivo')}, '4 días libres seguidos', FOOT)),
   (3.4, product_scene('Con todos los puentes marcados')),
   (2.0, endcard)],
 'diciembre': [
   (3.0, hook_scene('Pide 1 día de vacaciones y ten 5 libres', 'Diciembre de 2027')),
   (4.4, cal_scene('Puente de diciembre 2027', 12, {6: ('fest', 'Festivo'), 7: ('pide', 'Pide este día'), 8: ('fest', 'Festivo')},
                   'Del 4 al 8: 5 días libres', FOOT)),
   (3.6, product_scene('Calendario laboral 2027 para imprimir')),
   (2.0, endcard)],
 'findes': [
   (3.0, hook_scene('Los 4 fines de semana largos de 2027', 'Apúntalos ya')),
   (5.0, multi_scene('Fines de semana de 3 días', [
       ('1 ENE', ('Viernes · Año Nuevo', 'Del 1 al 3 de enero')),
       ('26 MAR', ('Viernes Santo', 'Semana Santa, del 26 al 28')),
       ('1 NOV', ('Lunes · Todos los Santos', 'Del 30 oct al 1 nov')),
       ('6 DIC', ('Lunes · Constitución', 'Y el 8 también es festivo'))])),
   (3.0, product_scene('Calendario laboral 2027 para imprimir')),
   (2.0, endcard)],
}

def render(key):
    out = S + f'cal/cal_{key}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPS), '-i', '-',
                          '-i', S+'vid/pop2.wav', '-shortest', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '160k', '-af', 'afade=t=out:st=13.4:d=1.5', out], stdin=subprocess.PIPE)
    prev = None; cover = None
    for si, (dur, fn) in enumerate(R[key]):
        n = int(round(dur*FPS))
        for i in range(n):
            fr = fn(i/max(1, n-1))
            if prev is not None and i < 7: fr = Image.blend(prev, fr, (i+1)/8)
            if si == 0 and i == n-5: cover = fr
            p.stdin.write(fr.tobytes())
        prev = fn(1.0)
    p.stdin.close(); p.wait()
    cover.save(S + f'cal/cover_{key}.jpg', quality=90)
    if len(sys.argv) > 2:
        for si, (dur, fn) in enumerate(R[key]): fn(1.0).save(S + f'cal/chk_{key}_{si}.jpg', quality=80)
    print(out)

render(sys.argv[1])
