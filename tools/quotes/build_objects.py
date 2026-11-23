"""Worth sending v4 (23 Nov 2026): each quote drawn as an everyday object.
Receipt, lock screen, light switch, out-of-office reply. Brand colours and fonts (Nunito, Roboto, Roboto Mono); no stock imagery."""
import sys, os, base64
sys.path.insert(0, '/home/claude/ig')
from common import FONTS, white_b64, primary_b64

def mono(w):
    b = base64.b64encode(open(f'/home/claude/ig/node_modules/@fontsource/roboto-mono/files/roboto-mono-latin-{w}-normal.woff2', 'rb').read()).decode()
    return f"@font-face{{font-family:'RMono';font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2');}}"

F = FONTS + mono(400) + mono(500) + mono(700)
Y, PY, CR, NB, TL, WH, WG = '#F2BE1A', '#FFF6E0', '#F7F5EB', '#1A1A1A', '#2A7469', '#FFFFFF', '#6E6862'
OUT = '/home/claude/ig/quotes/objhtml'
os.makedirs(OUT, exist_ok=True)


def doc(w, h, bg, body, css=''):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{F}"
            f"*{{margin:0;padding:0;box-sizing:border-box}}html,body{{-webkit-font-smoothing:antialiased}}"
            f"body{{width:{w}px;height:{h}px}}.slide{{width:{w}px;height:{h}px;position:relative;overflow:hidden;background:{bg};font-family:Roboto,sans-serif}}"
            f".nun{{font-family:Nunito,sans-serif;font-weight:900;letter-spacing:-.03em;line-height:1.02}}"
            f".mono{{font-family:RMono,monospace}}"
            f".mark{{position:absolute;left:0;right:0;text-align:center;font-family:Nunito,sans-serif;font-weight:900;font-size:22px;letter-spacing:.24em;text-transform:uppercase}}"
            f"{css}</style></head><body><div class='slide'>{body}</div></body></html>")


def mark(no, col, top=70):
    return f"<div class='mark' style='top:{top}px;color:{col}'>Worth sending &middot; No. {no:02d}</div>"


def sig(col, bottom=64, logo=None):
    inner = (f"<img src='data:image/png;base64,{logo}' style='height:50px'>" if logo else
             f"<span style='font-family:Nunito,sans-serif;font-weight:900;font-size:28px;color:{col}'>equal psychology</span>")
    return f"<div style='position:absolute;left:0;right:0;bottom:{bottom}px;display:flex;justify-content:center'>{inner}</div>"


# ---------- 1. Receipt ----------
def receipt(H=1350, top=150):
    rows = [("Finished everything", "NOT NEEDED"), ("Inbox at zero", "NOT NEEDED"),
            ("Proved you deserved it", "NOT NEEDED"), ("Felt guilty first", "NOT NEEDED")]
    lines = ''.join(f"<div class='row'><span>{a}</span><i></i><span>{b}</span></div>" for a, b in rows)
    bars = ''.join(f"<b style='width:{w}px'></b>" for w in [4, 2, 6, 2, 3, 8, 2, 4, 2, 6, 3, 2, 8, 4, 2, 3, 6, 2, 4, 8, 2, 3, 2, 6, 4, 2, 8, 3, 2, 4, 6, 2])
    css = """
.paper{position:absolute;left:170px;width:740px;background:#FFFDF7;transform:rotate(-2.2deg);
  box-shadow:0 30px 60px rgba(26,26,26,.18),0 6px 14px rgba(26,26,26,.10);padding:58px 60px 70px;color:#1A1A1A}
.paper:after{content:'';position:absolute;left:0;right:0;bottom:-22px;height:24px;
  background:linear-gradient(-45deg,transparent 12px,#FFFDF7 0) 0 0/24px 24px repeat-x,linear-gradient(45deg,transparent 12px,#FFFDF7 0) 0 0/24px 24px repeat-x}
.hd{text-align:center;font-size:26px;letter-spacing:.3em;font-weight:700}
.sub{text-align:center;font-size:21px;color:#6E6862;margin-top:12px;letter-spacing:.06em}
.dash{border-top:3px dashed #1A1A1A;margin:30px 0;opacity:.7}
.row{display:flex;align-items:baseline;gap:12px;font-size:25px;margin:16px 0}
.row i{flex:1;border-bottom:3px dotted rgba(26,26,26,.35);transform:translateY(-6px)}
.row span:last-child{font-weight:700}
.tot{display:flex;justify-content:space-between;font-size:34px;font-weight:700}
.bar{display:flex;gap:4px;height:70px;justify-content:center;margin-top:34px}.bar b{background:#1A1A1A;display:block}
"""
    body = (mark(1, NB, 64 if H == 1350 else 230) +
            f"<div class='paper mono' style='top:{top}px'>"
            f"<div class='hd'>REST &middot; RECEIPT</div><div class='sub'>No. 0001 &nbsp; 01/12 &nbsp; 5:31 PM</div>"
            f"<div class='dash'></div>{lines}<div class='dash'></div>"
            f"<div class='tot'><span>TOTAL OWED</span><span>$0.00</span></div>"
            f"<div class='nun' style='font-size:84px;margin-top:44px;letter-spacing:-.035em'>You don&rsquo;t have to earn a rest.</div>"
            f"<div class='bar'>{bars}</div>"
            f"<div class='sub' style='margin-top:14px'>KEEP THIS RECEIPT</div></div>" +
            sig(NB, 52 if H == 1350 else 330))
    return doc(1080, H, Y, body, css)


# ---------- 2. Lock screen ----------
NOTES = [("Work email", "now", "Quick one before tomorrow?"),
         ("Project chat", "2m", "Just circling back on this"),
         ("Work email", "9m", "Can you send it tonight?"),
         ("Team thread", "14m", "12 new messages")]


def lock(n_notes=4, dim=False, quote=True, H=1920, no=2):
    css = """
.sky{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 0%,#3C8E81 0%,#2A7469 45%,#1F5951 100%)}
.moon{position:absolute;right:150px;width:120px;height:120px;border-radius:50%;background:#FFF6E0;box-shadow:0 0 80px rgba(255,246,224,.35)}
.moon:after{content:'';position:absolute;left:-34px;top:-20px;width:120px;height:120px;border-radius:50%;background:#2F7C70}
.time{position:absolute;left:0;right:0;text-align:center;color:#FFF6E0;font-family:Nunito,sans-serif;font-weight:700;letter-spacing:-.04em}
.date{position:absolute;left:0;right:0;text-align:center;color:rgba(255,246,224,.85);font-size:32px;letter-spacing:.02em}
.n{background:rgba(255,253,247,.9);border-radius:38px;padding:34px 38px;margin-bottom:18px;color:#1A1A1A;display:flex;gap:24px;align-items:center}
.n .ic{width:66px;height:66px;border-radius:16px;background:#F2BE1A;flex:none;display:flex;align-items:center;justify-content:center;font-family:Nunito,sans-serif;font-weight:900;font-size:30px}
.n b{font-size:31px;display:flex;justify-content:space-between}.n b em{font-style:normal;font-weight:400;color:#6E6862;font-size:24px}
.n p{font-size:34px;margin-top:6px}
.q{position:absolute;left:80px;right:150px;color:#FFFFFF}
"""
    reel = H == 1920
    t_top = 330 if reel else 150
    notes = ''.join(f"<div class='n'><div class='ic'>{a[0]}</div><div style='flex:1'><b>{a}<em>{t}</em></b><p>{m}</p></div></div>"
                    for a, t, m in NOTES[:n_notes][::-1])
    stack_top = t_top + 330
    body = ("<div class='sky'></div>" + f"<div class='moon' style='top:{t_top - 60}px'></div>" +
            mark(no, Y, 230 if reel else 64) +
            f"<div class='time' style='top:{t_top}px;font-size:210px'>10:47</div>"
            f"<div class='date' style='top:{t_top + 240}px'>Tuesday 2 December</div>"
            f"<div style='position:absolute;left:80px;right:{150 if reel else 80}px;top:{stack_top}px;opacity:{.28 if dim else 1};filter:{'blur(1.5px)' if dim else 'none'}'>{notes}</div>")
    if quote:
        body += (f"<div class='q' style='top:{stack_top + 40}px'><div class='nun' style='font-size:118px'>"
                 f"Not every message needs an answer <span style='color:#F2BE1A'>tonight.</span></div></div>")
    body += sig(PY, 360 if reel else 60, white_b64)
    return doc(1080, H, TL, body, css)


# ---------- 3. Light switch ----------
def switch(H=1350):
    css = """
.wall{position:absolute;inset:0;background:radial-gradient(70% 55% at 50% 42%,#FFFDF7 0%,#F7F5EB 55%,#ECE8DA 100%)}
.plate{position:absolute;left:50%;top:210px;width:400px;height:620px;margin-left:-200px;border-radius:44px;background:linear-gradient(160deg,#FFFFFF,#F1EEE4);
  box-shadow:0 40px 70px rgba(26,26,26,.16),0 8px 18px rgba(26,26,26,.08),inset 0 2px 0 #fff}
.screw{position:absolute;left:50%;width:30px;height:30px;margin-left:-15px;border-radius:50%;background:linear-gradient(135deg,#E2DED2,#C9C4B6)}
.screw:after{content:'';position:absolute;left:6px;right:6px;top:13px;height:4px;background:#A9A394;border-radius:2px;transform:rotate(30deg)}
.well{position:absolute;left:50%;top:150px;width:200px;height:320px;margin-left:-100px;border-radius:30px;background:#E9E5D9;box-shadow:inset 0 6px 14px rgba(26,26,26,.15)}
.rock{position:absolute;left:12px;right:12px;top:12px;bottom:12px;border-radius:22px;background:linear-gradient(180deg,#E7E3D7 0%,#FFFFFF 46%,#F2BE1A 46.5%,#E6B10F 100%);
  box-shadow:0 -10px 20px rgba(26,26,26,.10)}
.lab{position:absolute;left:0;right:0;bottom:46px;text-align:center;font-family:Nunito,sans-serif;font-weight:900;font-size:40px;letter-spacing:.12em;color:#1A1A1A}
"""
    body = ("<div class='wall'></div>" + mark(3, TL, 64) +
            "<div class='plate'><div class='screw' style='top:56px'></div><div class='well'><div class='rock'>"
            "<div class='lab'>OFF</div></div></div><div class='screw' style='bottom:56px'></div></div>"
            "<div class='nun' style='position:absolute;left:0;right:0;top:890px;text-align:center;font-size:132px;color:#1A1A1A'>Off means off.</div>" +
            sig(TL, 60, primary_b64))
    return doc(1080, H, CR, body, css)


# ---------- 4. Out-of-office reply ----------
def ooo(stage=3, H=1920):
    css = """
.win{position:absolute;left:70px;right:70px;background:#FFFFFF;border-radius:30px;box-shadow:0 40px 80px rgba(26,26,26,.16),0 8px 20px rgba(26,26,26,.08);overflow:hidden}
.bar{height:70px;background:#F7F5EB;display:flex;align-items:center;gap:14px;padding:0 30px}.bar i{width:20px;height:20px;border-radius:50%;background:#DCD7C9;display:block}
.f{padding:30px 50px;border-bottom:2px solid #F0ECE0;font-size:34px;color:#6E6862}.f b{color:#1A1A1A;font-weight:500}
.tag{display:inline-block;background:#2A7469;color:#fff;font-family:Nunito,sans-serif;font-weight:900;font-size:22px;letter-spacing:.1em;padding:8px 18px;border-radius:999px;margin-left:12px;vertical-align:middle}
.b{padding:56px 50px 64px;font-size:46px;line-height:1.45;color:#1A1A1A}
.hl{background:linear-gradient(transparent 52%,#F2BE1A 52%,#F2BE1A 94%,transparent 94%);padding:0 4px}
.cur{display:inline-block;width:4px;height:44px;background:#2A7469;vertical-align:-8px;margin-left:4px}
"""
    reel = H == 1920
    top = 400 if reel else 200
    l1 = "Thanks for your message."
    l2 = "I&rsquo;ve logged off for the day."
    l3 = "<span class='hl nun' style='font-size:78px;line-height:1.1;letter-spacing:-.02em'>Logging off is part of the job.</span>" if stage >= 3 else ''
    l4 = "I&rsquo;ll reply tomorrow, rested." if stage >= 3 else ''
    body_txt = l1 + ("<br><br>" + l2 if stage >= 2 else "<span class='cur'></span>") + \
        ("<span class='cur'></span>" if stage == 2 else '') + \
        (f"<br><br>{l3}<br><br>{l4}" if stage >= 3 else '')
    body = (mark(4, TL, 230 if reel else 64) +
            f"<div class='win' style='top:{top}px'><div class='bar'><i></i><i></i><i></i></div>"
            f"<div class='f'>Subject: <b>Automatic reply</b><span class='tag'>OUT OF OFFICE</span></div>"
            f"<div class='f'>From: <b>Me</b> &nbsp;&nbsp; To: <b>Everyone, after 5:30</b></div>"
            f"<div class='b'>{body_txt}</div></div>" + sig(TL, 360 if reel else 60, primary_b64))
    return doc(1080, H, PY, body, css)


def endcard(no, send, bg=TL):
    body = (f"<div style='position:absolute;left:80px;right:150px;top:330px;bottom:430px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>"
            f"<img src='data:image/png;base64,{white_b64}' style='width:360px'>"
            f"<div style='width:64px;height:6px;border-radius:3px;background:{Y};margin:56px 0 48px'></div>"
            f"<div class='nun' style='font-size:56px;line-height:1.12;color:#fff;text-wrap:balance'>{send}</div>"
            f"<div style='font-family:Nunito,sans-serif;font-weight:900;font-size:24px;letter-spacing:.24em;text-transform:uppercase;margin-top:44px;color:{Y}'>Worth sending &middot; No. {no:02d}</div>"
            f"<div style='font-size:22px;margin-top:26px;color:rgba(255,255,255,.8)'>General information only, not psychological advice.</div></div>"
            f"<div style='position:absolute;left:0;right:0;bottom:360px;text-align:center;color:rgba(255,255,255,.8);font-size:24px'>@equal_psychology</div>")
    return doc(1080, 1920, bg, body)


if __name__ == '__main__':
    w = lambda n, h: open(f'{OUT}/{n}.html', 'w').write(h)
    w('S_2026-12-01-receipt', receipt())
    w('S_2026-12-03-switch', switch())
    # Reel 2 Dec: notifications pile up, then dim, then the line
    w('R_2026-12-02-lock_F1', lock(1, quote=False))
    w('R_2026-12-02-lock_F2', lock(4, quote=False))
    w('R_2026-12-02-lock_F3', lock(0, quote=True))
    w('R_2026-12-02-lock_F4', endcard(2, "Send this to someone still answering emails at 10pm.", bg=CR.replace(CR, TL)))
    # Reel 4 Dec: the auto-reply types out
    w('R_2026-12-04-ooo_F1', ooo(1))
    w('R_2026-12-04-ooo_F2', ooo(2))
    w('R_2026-12-04-ooo_F3', ooo(3))
    w('R_2026-12-04-ooo_F4', endcard(4, "Send this to the colleague who never logs off."))
    print('ok')
