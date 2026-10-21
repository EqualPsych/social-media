import os,sys
from PIL import Image,ImageDraw
SM='/home/claude/social-media/instagram/'
KEEP={'2026-11-03':SM+'2026-11/2026-11-03-less-harsh-carousel/slide-1.png','2026-11-17':SM+'2026-11/2026-11-17-fear-of-compassion-carousel/slide-1.png'}
dates=['2026-10-23','2026-11-03','2026-11-13','2026-11-17','2026-11-27','2026-12-08','2026-12-16']
W,H=360,450
def row(ds,out):
    s=Image.new('RGB',(W*8,H*len(ds)),'white')
    for r,d in enumerate(ds):
        for i in range(1,9):
            p=f'png/C_{d}_{i}.png'
            if not os.path.exists(p): p=KEEP[d]
            s.paste(Image.open(p).convert('RGB').resize((W-6,H-6)),(i*W-W,r*H))
    s.save(out)
row(dates[:4],'sheet1.png');row(dates[4:],'sheet2.png')
s=Image.new('RGB',(W*4,H),'white')
for i,d in enumerate(['2026-10-24','2026-10-28','2026-12-12','2026-12-20']): s.paste(Image.open(f'png/S_{d}.png').convert('RGB').resize((W-6,H-6)),(i*W,0))
s.save('singles.png')
