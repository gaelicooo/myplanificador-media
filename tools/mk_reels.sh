set -e
mk(){ # a b out
ffmpeg -y -loglevel error -loop 1 -t 6 -i $1 -loop 1 -t 6 -i $2 -loop 1 -t 3.5 -i end.jpg -i xmas.wav -filter_complex "\
[0]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=180:s=1080x1920:fps=30,setsar=1[a];\
[1]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=180:s=1080x1920:fps=30,setsar=1[b];\
[2]scale=1080:1920,fps=30,setsar=1[c];\
[a][b]xfade=transition=fade:duration=0.6:offset=5.4[ab];[ab][c]xfade=transition=fade:duration=0.6:offset=10.8[v]" \
-map "[v]" -map 3:a -shortest -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart $3
}
mk mandalas.jpg mandalas_b.jpg mandalas.mp4
mk dibujos.jpg dibujos_b.jpg dibujos.mp4
mk pack_navidad.jpg pack_navidad_b.jpg pack_navidad.mp4
M=/home/claude/myplanificador-media/videos
for n in reyes papanoel etiquetas; do ffmpeg -y -loglevel error -i $M/$n.mp4 -i xmas.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart ${n}.mp4; done
for n in presupuesto geometria; do ffmpeg -y -loglevel error -i $M/$n.mp4 -i neutral.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart ${n}.mp4; done
for f in *.mp4; do echo "$f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)"; done
ffmpeg -y -loglevel error -ss 2 -i mandalas.mp4 -frames:v 1 -vf scale=270:-1 t1.png; ffmpeg -y -loglevel error -ss 8 -i dibujos.mp4 -frames:v 1 -vf scale=270:-1 t2.png; ffmpeg -y -loglevel error -ss 12.5 -i pack_navidad.mp4 -frames:v 1 -vf scale=270:-1 t3.png
ffmpeg -y -loglevel error -i t1.png -i t2.png -i t3.png -filter_complex hstack=3 sheet.png
