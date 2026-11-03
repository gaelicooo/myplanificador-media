from PIL import Image, ImageDraw, ImageFont
M='/home/claude/myplanificador-media/pins/'
FB='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; FM='/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
def canvas(pin,out):
    p=Image.open(M+pin).convert('RGB'); bg=p.getpixel((15,15))
    c=Image.new('RGB',(1080,1920),bg); c.paste(p.resize((1080,1620),Image.LANCZOS),(0,150)); c.save(out,quality=95)
def endcard(bg,fg,out):
    c=Image.new('RGB',(1080,1920),bg); d=ImageDraw.Draw(c)
    icon=Image.open(M+'pin_reyes.jpg').crop((600,1335,680,1415)).resize((200,200))
    m=Image.new('L',(200,200),0); ImageDraw.Draw(m).rounded_rectangle((0,0,199,199),40,fill=255); c.paste(icon,(440,560),m)
    for t,f,y,col in [('MyPlanificador',ImageFont.truetype(FB,84),830,fg),('Imprimibles en español',ImageFont.truetype(FM,48),950,fg),
                      ('-20 % con BIENVENIDA20',ImageFont.truetype(FB,60),1150,(233,196,106)),('Búscanos en Etsy',ImageFont.truetype(FM,48),1260,fg)]:
        w=d.textlength(t,font=f); d.text(((1080-w)/2,y),t,font=f,fill=col)
    c.save(out,quality=95)
for n in ['mandalas','mandalas_b','dibujos','dibujos_b','pack_navidad','pack_navidad_b']: canvas(f'pin_{n}.jpg',f'{n}.jpg')
endcard((28,37,70),(255,255,255),'end.jpg')
