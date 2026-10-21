# Re-cut Reels with rotated hook colours (22 Oct 2026). Text, timings and audio unchanged.
import sys, re
sys.path.insert(0,'/home/claude/ig'); sys.path.insert(0,'/home/claude/ig/reels')
import common; common.WG='#6E6862'
from common import *
WG='#6E6862'
OUT='/home/claude/ig/recut/html'
S={'NB':(NB,WH,Y,Y,'rgba(255,255,255,.25)'),'Y':(Y,NB,NB,NB,'rgba(26,26,26,.2)'),'TL':(TL,WH,Y,Y,'rgba(255,255,255,.3)'),
   'CR':(CR,NB,TL,TL,'rgba(26,26,26,.15)'),'PY':(PY,NB,TL,TL,'rgba(26,26,26,.15)')}
def plan(hook,n_text):
    seq=[hook,'Y']
    for opts in (['TL','NB','CR'],['CR','PY','TL','NB'],['PY','TL','CR','NB'])[:n_text-2]:
        seq.append(next(o for o in opts if o!=seq[-1] and o!=seq[-2] if True))
    seq.append('TL' if seq[-1]=='NB' else 'NB')   # end card: dark, white logo
    return seq
# --- Your brain's best guess
src=open('/home/claude/ig/reels/build_reels.py').read().split('for r in REELS')[0].replace("from common import FONTS, Y, PY, CR, NB, TL, WG, WH","from common import FONTS, Y, PY, CR, NB, TL, WH")
g={'WG':WG}; exec(src.replace("OUT='/home/claude/ig/reels/html'","OUT='/home/claude/ig/recut/html'"),g)
LAB=[None,'What research found','Why it might happen','Something to try',None]
BG={2:'TL',3:'TL',4:'TL',5:'PY',6:'CR'}
for r in g['REELS']:
    if r['n'] not in BG: continue
    seq=plan(BG[r['n']],4); print('r',r['n'],seq)
    g['FR']=[(*S[k],LAB[i]) for i,k in enumerate(seq)]
    for i in range(5): open(f"{OUT}/r{r['n']}_{i+1}.html",'w').write(g['frame'](i,r))
# --- ADHD: the full picture
a=open('/home/claude/ig/adhd/build_adhd.py').read()
a=a.split('# ---------- reels (1080x1920) ----------')[0].split('# ---------- carousel helpers')[0]+'\n'+a.split('# ---------- reels (1080x1920) ----------')[1].split('DUR=')[0]
h={}; exec(a.replace("from common import *","from common import *\nWG='#6E6862'"),h)
AB={'missed':'PY','ad':'CR','mistaken':'PY'}
for k,hk in AB.items():
    fr=h['R'][k]; n=len(fr); seq=plan(hk,n-1); print(k,seq)
    for i,f in enumerate(fr):
        if f[0]=='END': x=h['rframe'](i,n,seq[-1],None,None,end=f[1])
        else: x=h['rframe'](i,n,seq[i],f[1],f[2],size=f[3],sub=f[4])
        open(f'{OUT}/R_{k}_{i+1}.html','w').write(x)
