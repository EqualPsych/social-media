"""Still-frame companion Reel frames (1080x1920), "THE SHORT VERSION" style.
Rebuilt 24 Oct 2026 to match the existing companions (e.g. 30 Nov protocol): progress bars at y150,
eyebrow at y203, label then Nunito 900 headline (~86px) centred in the frame, handle at y1564."""
import sys, os
sys.path.insert(0, '/home/claude/ig')
from common import FONTS, white_b64

Y, PY, CR, NB, TL, WH = '#F2BE1A', '#FFF6E0', '#F7F5EB', '#1A1A1A', '#2A7469', '#FFFFFF'
# bg: (text, accent for bars/eyebrow/label, empty-bar colour, handle colour)
ST = {
    TL: (WH, Y, 'rgba(255,255,255,.3)', 'rgba(255,255,255,.75)'),
    Y:  (NB, NB, 'rgba(26,26,26,.2)', 'rgba(26,26,26,.55)'),
    PY: (NB, TL, 'rgba(26,26,26,.15)', '#6E6862'),
    CR: (NB, TL, 'rgba(26,26,26,.15)', '#6E6862'),
    NB: (WH, Y, 'rgba(255,255,255,.25)', 'rgba(255,255,255,.6)'),
}
CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;-webkit-font-smoothing:antialiased}
.slide{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'Roboto',sans-serif}
.bars{position:absolute;top:150px;left:80px;right:81px;display:flex;gap:12px}
.bars i{flex:1;height:6px;border-radius:3px;display:block}
.eye{position:absolute;top:200px;left:80px;font-family:'Nunito',sans-serif;font-weight:800;font-size:26px;letter-spacing:.1em;text-transform:uppercase}
.box{position:absolute;left:80px;right:150px;top:330px;bottom:430px;display:flex;flex-direction:column;justify-content:center}
.lab{font-family:'Nunito',sans-serif;font-weight:800;font-size:28px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:26px}
h1{font-family:'Nunito',sans-serif;font-weight:900;letter-spacing:-.015em;line-height:1.06;text-wrap:pretty}
.handle{position:absolute;top:1560px;left:80px;font-size:26px}
"""


def frame(i, n, bg, label=None, text=None, size=86, end=None):
    tx, ac, empty, hc = ST[bg]
    bars = ''.join(f"<i style='background:{ac if k <= i else empty}'></i>" for k in range(n))
    if end:
        body = (f"<img src='data:image/png;base64,{white_b64}' style='width:380px;display:block'>"
                f"<div style='width:64px;height:5px;background:{Y};margin:52px 0 40px;border-radius:3px'></div>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:900;font-size:50px;line-height:1.15;color:{WH}'>{end['title']}</p>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:800;font-size:36px;margin-top:26px;color:{Y}'>{end['line']}</p>"
                f"<p style='font-size:28px;margin-top:30px;color:{WH}'>{end['source']}</p>"
                f"<p style='font-size:22px;margin-top:20px;color:rgba(255,255,255,.75)'>General information only, not psychological advice.</p>")
    else:
        body = (f"<div class='lab' style='color:{ac}'>{label}</div>"
                f"<h1 style='font-size:{size}px;color:{tx}'>{text}</h1>")
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='slide' style='background:{bg}'><div class='bars'>{bars}</div>"
            f"<div class='eye' style='color:{ac}'>The short version</div>"
            f"<div class='box'>{body}</div><div class='handle' style='color:{hc}'>@equal_psychology</div></div></body></html>")


C = {
    'grief-at-christmas': [
        (TL, 'Grief at Christmas', "Most of us carry a timetable for grief.", 96),
        (Y, 'What research shows', "Among older widowed adults, distress rose around a late partner's birthday and in January, after the holidays.", 80),
        (PY, 'Why it matters', "How much it hurts on one day tells you very little. What matters is the shape of grief across months.", 82),
        (CR, 'Something to try', "This week, notice whether the longing comes in waves around certain days, or stays the same most of the time.", 78),
        (TL, None, None, None),
    ],
}
END = {'grief-at-christmas': dict(title='Grief at Christmas', line='The full carousel is on our profile',
                                  source='Source: Carr et al., 2014')}

if __name__ == '__main__':
    slug = sys.argv[1]
    out = f'/home/claude/ig/comp/html_{slug}'
    os.makedirs(out, exist_ok=True)
    fr = C[slug]
    for i, (bg, lab, txt, size) in enumerate(fr):
        h = frame(i, len(fr), bg, lab, txt, size or 86, end=END[slug] if lab is None else None)
        open(f'{out}/F{i + 1}.html', 'w').write(h)
    print('ok', len(fr))
