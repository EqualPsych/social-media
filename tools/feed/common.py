import base64, os

ROOT = '/home/claude/ig'
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)
SLUG = 'Stoicism'

white_b64 = open(f'{ROOT}/logo_white_b64.txt').read().strip()
primary_b64 = open(f'{ROOT}/logo_yellow_b64.txt').read().strip()


def font(pkg, fam, w):
    p = f'{ROOT}/node_modules/@fontsource/{pkg}/files/{pkg}-latin-{w}-normal.woff2'
    b = base64.b64encode(open(p, 'rb').read()).decode()
    return (f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;"
            f"src:url(data:font/woff2;base64,{b}) format('woff2');}}")


FONTS = ''.join([font('nunito', 'Nunito', w) for w in (400, 700, 900)] +
                [font('roboto', 'Roboto', w) for w in (300, 400, 500)])

Y, PY, CR, NB, TL, WG, WH = '#F2BE1A', '#FFF6E0', '#F7F5EB', '#1A1A1A', '#2A7469', '#8A8480', '#FFFFFF'
HANDLE = '@equal_psychology'

BASE = FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{-webkit-font-smoothing:antialiased;}}
body{{width:1160px;height:%(H)spx;background:#FF0000;display:flex;align-items:center;justify-content:center;}}
.slide{{width:1080px;height:%(SH)spx;position:relative;overflow:hidden;flex-shrink:0;font-family:'Roboto',sans-serif;}}
.top{{position:absolute;top:72px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:center;}}
.num{{font-weight:500;font-size:20px;letter-spacing:.1em;}}
.eyebrow{{font-family:'Nunito',sans-serif;font-weight:700;font-size:22px;letter-spacing:.1em;text-transform:uppercase;}}
.pill{{font-family:'Nunito',sans-serif;font-weight:700;font-size:20px;letter-spacing:.1em;text-transform:uppercase;padding:12px 26px;border-radius:999px;}}
.content{{position:absolute;left:88px;right:88px;top:170px;bottom:150px;display:flex;flex-direction:column;justify-content:center;}}
h1{{font-family:'Nunito',sans-serif;font-weight:900;letter-spacing:-.025em;line-height:1.04;}}
.rule{{width:52px;height:4px;border-radius:2px;background:{Y};}}
.foot{{position:absolute;bottom:64px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:center;font-size:22px;}}
.stripe{{position:absolute;top:0;left:0;right:0;height:8px;}}
p{{font-size:32px;line-height:1.45;font-weight:400;text-wrap:pretty;}}
h1{{text-wrap:balance;}}
"""


def page(body, css='', bg=CR, square=False):
    dims = {'H': 1160 if square else 1430, 'SH': 1080 if square else 1350}
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><style>{BASE % dims}{css}"
            f".slide{{background:{bg};}}</style></head><body><div class='slide'>{body}</div></body></html>")


def top(n, col, left=''):
    return f"<div class='top'><div>{left}</div><div class='num' style='color:{col}'>0{n} / 08</div></div>"


def foot(col, right=''):
    return f"<div class='foot' style='color:{col}'><div>{HANDLE}</div><div>{right}</div></div>"

