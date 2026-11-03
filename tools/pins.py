import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = '/home/claude/myplanificador-media/'
SP = '/tmp/claude-0/-home-claude/df77763c-98f1-5abe-be30-12ac4f1d7d46/scratchpad/'
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
FM = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
FSB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
W, H = 1000, 1500
NAVY = (28, 37, 70); RED = (195, 38, 45); GREEN = (31, 107, 79); CREAM = (251, 246, 240)
GOLD = (233, 196, 106); DARK = (30, 30, 36)

def font(p, s):
    return ImageFont.truetype(p, s)

src = Image.open(REPO + 'pins/pin_reyes.jpg').convert('RGB')
ICON = src.crop((600, 1335, 680, 1415))

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def base(bg, title, sub, fg=(255, 255, 255), subc=GOLD, accent=GOLD):
    im = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(im)
    # decorative circle top right (como los pines existentes)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    tint = (255, 255, 255, 18) if bg != CREAM else (0, 0, 0, 10)
    od.ellipse((620, -330, 1260, 310), fill=tint)
    im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
    ft = font(FB, 78); y = 95
    for ln in wrap(d, title, ft, 880):
        d.text((70, y), ln, font=ft, fill=fg); y += 92
    d.rounded_rectangle((70, y + 8, 170, y + 18), 5, fill=accent)
    y += 50
    fs = font(FM, 40)
    for ln in wrap(d, sub, fs, 860):
        d.text((70, y), ln, font=fs, fill=subc); y += 54
    # footer
    fp = font(FSB, 34); txt = 'Descarga instantánea'
    tw = d.textlength(txt, font=fp)
    pill_bg, pill_fg = (CREAM, DARK) if bg != CREAM else (DARK, GOLD)
    d.rounded_rectangle((70, 1340, 70 + tw + 70, 1415), 38, fill=pill_bg)
    d.text((105, 1356), txt, font=fp, fill=pill_fg)
    m = Image.new('L', ICON.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 79, 79), 16, fill=255)
    im.paste(ICON, (600, 1337), m)
    d.text((695, 1354), 'MyPlanificador', font=font(FB, 35), fill=fg if bg != CREAM else DARK)
    return im, d, y

def shadow_paste(im, card, xy, angle=0, radius=18):
    card = card.convert('RGBA')
    m = Image.new('L', card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, card.size[0]-1, card.size[1]-1), radius, fill=255)
    card.putalpha(m)
    if angle: card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', (card.size[0] + 60, card.size[1] + 60), (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: int(v * 0.35))
    sh.paste((0, 0, 0, 255), (30, 40), a)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(sh, (xy[0] - 30, xy[1] - 30), sh)
    im.paste(card, xy, card)

# ---------- mandalas ----------
def mandala(size, seed, colored=0.0, palette=None):
    rnd = random.Random(seed)
    S = size * 2
    im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im)
    c = S / 2; lw = max(3, S // 170)
    n = rnd.choice([8, 10, 12, 16])
    rings = []
    r = S * 0.47
    while r > S * 0.06:
        rings.append(r); r *= rnd.uniform(0.72, 0.84)
    fills = palette or [(196, 40, 52), (33, 110, 80), (230, 186, 80), (28, 45, 90)]
    for i, R in enumerate(rings):
        kind = rnd.choice(['petal', 'circle', 'arc', 'spike'])
        nn = n * rnd.choice([1, 2])
        col = fills[i % len(fills)] if rnd.random() < colored else None
        for k in range(nn):
            t = 2 * math.pi * k / nn
            if kind == 'petal':
                pts = []
                for s in range(0, 31):
                    u = s / 30
                    rr = R * (0.72 + 0.28 * math.sin(math.pi * u))
                    ang = t + (u - 0.5) * (2 * math.pi / nn) * 0.9
                    pts.append((c + rr * math.cos(ang), c + rr * math.sin(ang)))
                inner = R * 0.72
                pts.append((c + inner * math.cos(t), c + inner * math.sin(t)))
                d.polygon(pts, fill=col, outline='black', width=lw)
            elif kind == 'circle':
                rr = R * 0.13; x, y = c + R * 0.86 * math.cos(t), c + R * 0.86 * math.sin(t)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col, outline='black', width=lw)
            elif kind == 'spike':
                a1, a2 = t - math.pi / nn, t + math.pi / nn
                pts = [(c + R * 0.75 * math.cos(a1), c + R * 0.75 * math.sin(a1)), (c + R * math.cos(t), c + R * math.sin(t)),
                       (c + R * 0.75 * math.cos(a2), c + R * 0.75 * math.sin(a2))]
                d.polygon(pts, fill=col, outline='black', width=lw)
            else:
                rr = R * 0.2; x, y = c + R * 0.8 * math.cos(t), c + R * 0.8 * math.sin(t)
                d.arc((x - rr, y - rr, x + rr, y + rr), 0, 360, fill='black', width=lw)
        d.ellipse((c - R * 0.7, c - R * 0.7, c + R * 0.7, c + R * 0.7), outline='black', width=lw)
    # centro: estrella
    R = S * 0.05; pts = []
    for k in range(10):
        rr = R if k % 2 == 0 else R * 0.45; a = -math.pi / 2 + k * math.pi / 5
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    return im.resize((size, size), Image.LANCZOS)

def page(w, h, art, label=None, name_line=False):
    p = Image.new('RGB', (w, h), 'white'); d = ImageDraw.Draw(p)
    a = art.resize((int(w * 0.82), int(w * 0.82)), Image.LANCZOS) if art.size[0] == art.size[1] else art
    ax = (w - a.size[0]) // 2; ay = (h - a.size[1]) // 2 + (20 if name_line else 0)
    p.paste(a, (ax, ay))
    if name_line:
        f = font(FSB, int(w * 0.055)); d.text((int(w * .08), int(h * .05)), 'Nombre:', font=f, fill=DARK)
        d.line((int(w * .32), int(h * .05) + int(w * .065), int(w * .92), int(h * .05) + int(w * .065)), fill=(150, 150, 150), width=2)
    if label:
        f = font(FM, int(w * 0.04)); tw = d.textlength(label, font=f)
        d.text(((w - tw) / 2, h - int(h * .06)), label, font=f, fill=(120, 120, 120))
    return p

def pin_mandalas_a():
    im, d, y = base(GREEN, '50 mandalas de Navidad para colorear', 'De fácil a difícil · para adultos y jóvenes · PDF en español')
    p1 = page(420, 594, mandala(420, 3), 'Nivel fácil')
    p2 = page(420, 594, mandala(420, 11, colored=0.6), 'Nivel medio')
    p3 = page(420, 594, mandala(420, 27), 'Nivel difícil')
    shadow_paste(im, p1, (60, 650), 6)
    shadow_paste(im, p3, (520, 640), -6)
    shadow_paste(im, p2, (290, 600), 0)
    return im

def pin_mandalas_b():
    im, d, y = base(CREAM, 'Tu momento antiestrés estas Navidades', '50 mandalas navideños para imprimir y colorear con calma', fg=DARK, subc=GREEN, accent=RED)
    p = page(640, 640, mandala(640, 42, colored=0.55))
    shadow_paste(im, p, (180, 620), -3)
    return im

# ---------- dibujos para colorear ----------
def star(d, cx, cy, R, lw, fill=None):
    pts = []
    for k in range(10):
        rr = R if k % 2 == 0 else R * 0.42; a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline='black', width=lw)

def draw_tree(S, colored=False):
    im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im); lw = S // 90
    g = (33, 110, 80) if colored else None
    for i, (top, bot, half) in enumerate([(0.18, 0.42, 0.22), (0.32, 0.6, 0.3), (0.48, 0.8, 0.38)]):
        d.polygon([(S/2, S*top), (S/2 - S*half, S*bot), (S/2 + S*half, S*bot)], fill=g, outline='black', width=lw)
    d.rectangle((S*0.44, S*0.8, S*0.56, S*0.92), fill=(140, 90, 50) if colored else None, outline='black', width=lw)
    star(d, S/2, S*0.15, S*0.08, lw, (230, 186, 80) if colored else None)
    for (x, y, c) in [(0.42, 0.38, RED), (0.58, 0.52, (230, 186, 80)), (0.36, 0.7, (40, 70, 160)), (0.62, 0.72, RED), (0.5, 0.6, (40, 70, 160))]:
        r = S * 0.03; d.ellipse((S*x - r, S*y - r, S*x + r, S*y + r), fill=c if colored else 'white', outline='black', width=lw)
    return im

def draw_snowman(S, colored=False):
    im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im); lw = S // 90
    d.ellipse((S*.26, S*.48, S*.74, S*.94), fill='white', outline='black', width=lw)
    d.ellipse((S*.33, S*.2, S*.67, S*.54), fill='white', outline='black', width=lw)
    d.rectangle((S*.36, S*.08, S*.64, S*.22), fill=DARK if colored else None, outline='black', width=lw)
    d.rectangle((S*.3, S*.2, S*.7, S*.25), fill=DARK if colored else None, outline='black', width=lw)
    d.rectangle((S*.33, S*.47, S*.67, S*.53), fill=RED if colored else None, outline='black', width=lw)
    d.polygon([(S*.5, S*.36), (S*.62, S*.39), (S*.5, S*.41)], fill=(240, 130, 40) if colored else None, outline='black', width=lw)
    for x in (0.44, 0.56):
        r = S*.018; d.ellipse((S*x-r, S*.31-r, S*x+r, S*.31+r), fill='black')
    for yy in (0.62, 0.72, 0.82):
        r = S*.02; d.ellipse((S*.5-r, S*yy-r, S*.5+r, S*yy+r), fill='black')
    d.line((S*.27, S*.62, S*.1, S*.5), fill='black', width=lw); d.line((S*.73, S*.62, S*.9, S*.5), fill='black', width=lw)
    return im

def draw_gift(S, colored=False):
    im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im); lw = S // 90
    d.rectangle((S*.18, S*.42, S*.82, S*.9), fill=RED if colored else None, outline='black', width=lw)
    d.rectangle((S*.13, S*.3, S*.87, S*.44), fill=RED if colored else None, outline='black', width=lw)
    d.rectangle((S*.45, S*.3, S*.55, S*.9), fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    d.ellipse((S*.26, S*.12, S*.5, S*.32), fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    d.ellipse((S*.5, S*.12, S*.74, S*.32), fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    return im

def draw_crown(S, colored=False):
    im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im); lw = S // 90
    pts = [(S*.12, S*.75), (S*.12, S*.32), (S*.31, S*.52), (S*.5, S*.22), (S*.69, S*.52), (S*.88, S*.32), (S*.88, S*.75)]
    d.polygon(pts, fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    d.rectangle((S*.12, S*.72, S*.88, S*.86), fill=(230, 186, 80) if colored else None, outline='black', width=lw)
    for x, c in [(0.3, RED), (0.5, (40, 70, 160)), (0.7, (33, 110, 80))]:
        r = S*.045; d.ellipse((S*x-r, S*.79-r, S*x+r, S*.79+r), fill=c if colored else None, outline='black', width=lw)
    for x, y in [(0.12, 0.3), (0.5, 0.2), (0.88, 0.3)]:
        r = S*.04; d.ellipse((S*x-r, S*y-r, S*x+r, S*y+r), fill='white', outline='black', width=lw)
    return im

def pin_dibujos_a():
    im, d, y = base(RED, '60 dibujos de Navidad para colorear', 'Con el nombre de cada niño · Infantil y primaria · PDF en español')
    p1 = page(400, 566, draw_snowman(330), name_line=True)
    p2 = page(400, 566, draw_tree(330, colored=True), name_line=True)
    p3 = page(400, 566, draw_crown(330), name_line=True)
    shadow_paste(im, p1, (60, 660), 6)
    shadow_paste(im, p3, (540, 650), -6)
    shadow_paste(im, p2, (300, 610), 0)
    return im

def pin_dibujos_b():
    im, d, y = base(NAVY, 'Plan para las vacaciones de Navidad', 'Árboles, muñecos de nieve, regalos, Reyes Magos y Papá Noel')
    tiles = [draw_tree(300), draw_gift(300, True), draw_snowman(300), draw_crown(300, True)]
    xs = [(90, 580), (530, 580), (90, 950), (530, 950)]
    for t, (x, yy) in zip(tiles, xs):
        shadow_paste(im, page(380, 340, t.resize((290, 290))), (x, yy), 0, 22)
    return im

# ---------- pack navideño ----------
def pin_pack_a():
    im, d, y = base(NAVY, 'Pack de Navidad para imprimir', 'Carta a los Reyes Magos + carta a Papá Noel + 68 etiquetas de regalo')
    crops = [Image.open(SP + f'crop_{n}.png') for n in ('reyes', 'papanoel', 'etiquetas')]
    shadow_paste(im, crops[1].resize((470, 409)), (480, 590), -4, 26)
    shadow_paste(im, crops[2].resize((470, 409)), (60, 860), 4, 26)
    shadow_paste(im, crops[0].resize((470, 409)), (60, 560), 3, 26)
    # sello de precio/ahorro
    d = ImageDraw.Draw(im)
    d.ellipse((640, 1020, 920, 1300), fill=GOLD)
    f1, f2 = font(FB, 50), font(FSB, 30)
    for t, f, yy in [('3 en 1', f1, 1100), ('mejor precio', f2, 1172)]:
        tw = d.textlength(t, font=f); d.text((780 - tw/2, yy), t, font=f, fill=NAVY)
    return im

def pin_pack_b():
    im, d, y = base(CREAM, 'La magia de Reyes y Papá Noel en un solo PDF', 'Cartas con sobre y respuesta, diplomas y 68 etiquetas para los regalos', fg=DARK, subc=RED, accent=RED)
    crops = [Image.open(SP + f'crop_{n}.png') for n in ('reyes', 'papanoel', 'etiquetas')]
    shadow_paste(im, crops[0].resize((560, 487)), (40, 640), -3, 26)
    shadow_paste(im, crops[1].resize((520, 452)), (430, 760), 4, 26)
    return im

out = {
    'pin_mandalas.jpg': pin_mandalas_a(), 'pin_mandalas_b.jpg': pin_mandalas_b(),
    'pin_dibujos.jpg': pin_dibujos_a(), 'pin_dibujos_b.jpg': pin_dibujos_b(),
    'pin_pack_navidad.jpg': pin_pack_a(), 'pin_pack_navidad_b.jpg': pin_pack_b(),
}
for n, im in out.items():
    im.save(REPO + 'pins/' + n, quality=92)
ims = [im.resize((400, 600)) for im in out.values()]
sheet = Image.new('RGB', (410 * len(ims), 600), 'gray')
for i, im in enumerate(ims): sheet.paste(im, (i * 410, 0))
sheet.save(SP + 'sheet.png')
print('ok')
