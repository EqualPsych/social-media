"""Feed redesign, 22 Oct 2026. Rebuilds upcoming carousels and singles to the standard Matt picked
(3 Nov carousel cover and 11 Nov single): topic pill, large headline, content centred on the page,
one yellow call-out word, and the skill's colour rotation (Section 4). Wording is unchanged.
<em>..</em> in a headline marks the call-out."""
import sys, os, re
sys.path.insert(0, '/home/claude/ig')
from common import FONTS, white_b64, primary_b64, HANDLE

OUT = '/home/claude/ig/redesign/html'
os.makedirs(OUT, exist_ok=True)
Y, PY, CR, NB, TL, WH = '#F2BE1A', '#FFF6E0', '#F7F5EB', '#1A1A1A', '#2A7469', '#FFFFFF'
WGR, GOLD = '#6E6862', '#7A5C00'

# per background: text, muted, eyebrow, rule, number/foot colour, card bg, card text, bullet
TH = {
    NB: dict(tx=WH, mu='rgba(255,255,255,.82)', eb=Y, rule=Y, ft='rgba(255,255,255,.6)', card=WH, ctx=NB, dot=Y, logo=white_b64),
    TL: dict(tx=WH, mu=WH, eb=Y, rule=Y, ft='rgba(255,255,255,.75)', card=WH, ctx=NB, dot=TL, logo=white_b64),
    Y:  dict(tx=NB, mu='rgba(26,26,26,.8)', eb=NB, rule=NB, ft='rgba(26,26,26,.7)', card=WH, ctx=NB, dot=Y, logo=None),
    CR: dict(tx=NB, mu=WGR, eb=TL, rule=TL, ft=WGR, card=WH, ctx=NB, dot=Y, logo=primary_b64),
    PY: dict(tx=NB, mu=WGR, eb=GOLD, rule=TL, ft=WGR, card=WH, ctx=NB, dot=Y, logo=primary_b64),
}

CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{-webkit-font-smoothing:antialiased}
body{width:1160px;height:1430px;background:#FF0000;display:flex;align-items:center;justify-content:center}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:'Roboto',sans-serif}
.top{position:absolute;top:64px;left:88px;right:88px;height:64px;display:flex;justify-content:space-between;align-items:center;z-index:2}
.num{font-weight:500;font-size:22px;letter-spacing:.12em}
.pill{font-family:'Nunito',sans-serif;font-weight:900;font-size:24px;letter-spacing:.1em;text-transform:uppercase;padding:13px 28px;border-radius:999px;background:#F2BE1A;color:#1A1A1A}
.content{position:absolute;left:88px;right:88px;top:170px;bottom:160px;display:flex;flex-direction:column;justify-content:center;z-index:2}
.content.low{justify-content:flex-end;padding-bottom:20px}
.eb{font-family:'Nunito',sans-serif;font-weight:900;font-size:24px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:30px}
h1{font-family:'Nunito',sans-serif;font-weight:900;letter-spacing:-.025em;line-height:1.06;text-wrap:balance}
p{font-size:37px;line-height:1.45;font-weight:400;text-wrap:pretty}
p.lt{font-weight:300}
.rule{width:56px;height:5px;border-radius:3px}
.foot{position:absolute;bottom:62px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:center;font-size:23px;z-index:2}
.card{border-radius:20px;padding:40px 44px}
.lab{font-family:'Nunito',sans-serif;font-weight:900;font-size:21px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:18px}
.li{display:flex;gap:26px;align-items:flex-start;padding:26px 34px;border-radius:18px;margin-bottom:16px}
.li i{flex:none;width:18px;height:18px;border-radius:50%;margin-top:15px}
.li span{font-size:34px;line-height:1.38}
.src{font-size:23px;letter-spacing:.02em;margin-top:34px;line-height:1.4}
.btn{display:inline-block;font-family:'Nunito',sans-serif;font-weight:900;font-size:26px;letter-spacing:.08em;text-transform:uppercase;padding:18px 40px;border-radius:999px}
"""


def em(h, bg):
    """Yellow call-out: yellow text on dark; a yellow highlighter band on light backgrounds (yellow text fails there)."""
    if bg in (NB, TL):
        return h.replace('<em>', f"<span style='color:{Y}'>").replace('</em>', '</span>')
    band = WH if bg == Y else Y
    return h.replace('<em>', f"<span style='background:linear-gradient(transparent 56%,{band} 56%,{band} 92%,transparent 92%);padding:0 6px;margin:0 -6px'>").replace('</em>', '</span>')


def page(bg, body, split=None):
    lay = ''
    if split:  # top 55% one colour, bottom 45% another
        lay = f"<div style='position:absolute;left:0;right:0;bottom:0;height:45%;background:{split}'></div>"
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body><div class='slide' style='background:{bg}'>{lay}{body}</div></body></html>")


def top(bg, n=None, pill=None, logo=False):
    t = TH[bg]
    left = f"<span class='pill'{' style=\"background:%s;color:%s\"' % (NB, Y) if bg == Y else ''}>{pill}</span>" if pill else '<span></span>'
    if logo and t['logo']:
        right = f"<img src='data:image/png;base64,{t['logo']}' style='height:64px;display:block'>"
    elif n:
        right = f"<span class='num' style='color:{t['ft']}'>{n:02d} / 08</span>"
    else:
        right = ''
    return f"<div class='top'>{left}{right}</div>"


def foot(bg, right='', rc=None):
    t = TH[bg]
    r = f"<span style='color:{rc or t['ft']}'>{right}</span>" if right else ''
    return f"<div class='foot' style='color:{t['ft']}'><span>{HANDLE}</span>{r}</div>"


def eb(bg, text):
    return f"<div class='eb' style='color:{TH[bg]['eb']}'>{text}</div>" if text else ''


def rule(bg, m='44px 0 40px'):
    return f"<div class='rule' style='background:{TH[bg]['rule']};margin:{m}'></div>"


def src(bg, s):
    return f"<p class='src' style='color:{TH[bg]['mu'] if bg != TL else 'rgba(255,255,255,.85)'}'>{s}</p>" if s else ''


def paras(bg, ps, size=37, first=0):
    t = TH[bg]
    return ''.join(f"<p class='lt' style='color:{t['mu'] if bg in (NB,) else t['tx']};font-size:{size}px;margin-top:{first if i == 0 else 26}px'>{p}</p>" for i, p in enumerate(ps))


# ---------- slide types ----------
def cover(bg, pill, h, sub, size=96):
    t = TH[bg]
    return page(bg, top(bg, 1, pill) +
                f"<div class='content'><h1 style='font-size:{size}px;color:{t['tx']}'>{em(h, bg)}</h1>{rule(bg, '48px 0 38px')}"
                f"<p class='lt' style='font-size:38px;color:{t['mu']}'>{sub}</p></div>" +
                foot(bg, 'Swipe to read &rarr;', TH[bg]['eb'] if bg in (NB, TL) else TH[bg]['tx']))


def single(bg, pill, h, sub, size=100, split=None):
    t = TH[bg]
    if split:  # headline in the top block, sub-line in the bottom block
        b = TH[split]
        return page(bg, top(bg, None, pill, logo=True) +
                    f"<div style='position:absolute;left:88px;right:88px;top:170px;height:540px;display:flex;flex-direction:column;justify-content:center'>"
                    f"<h1 style='font-size:{size}px;color:{t['tx']}'>{em(h, bg)}</h1></div>"
                    f"<div style='position:absolute;left:88px;right:88px;top:742px;bottom:160px;display:flex;flex-direction:column;justify-content:center'>"
                    f"{rule(split, '0 0 38px')}<p class='lt' style='font-size:40px;color:{b['tx']}'>{sub}</p></div>" +
                    foot(split, 'Kew &amp; Croydon, Melbourne'), split=split)
    return page(bg, top(bg, None, pill, logo=True) +
                f"<div class='content'><h1 style='font-size:{size}px;color:{t['tx']}'>{em(h, bg)}</h1>{rule(bg, '48px 0 38px')}"
                f"<p class='lt' style='font-size:39px;color:{t['mu']}'>{sub}</p></div>" +
                foot(bg, 'Kew &amp; Croydon, Melbourne'))


def statement(n, bg, e, h, ps, s=None, low=False, size=82, big=False):
    t = TH[bg]
    hs = 190 if big else size
    return page(bg, top(bg, n) +
                f"<div class='content{' low' if low else ''}'>{eb(bg, e)}<h1 style='font-size:{hs}px;color:{t['tx']}{';line-height:.95' if big else ''}'>{h}</h1>"
                f"{rule(bg)}{paras(bg, ps)}{src(bg, s)}</div>" + foot(bg))


def research(n, bg, e, h, ps, finding, s, size=80):
    """Finding in a card. On Yellow the card is white; on dark it is a translucent panel."""
    t = TH[bg]
    if bg in (Y, CR, PY):
        cs = f"background:{WH};color:{NB}"
    else:
        cs = f"background:rgba(255,255,255,.12);color:{WH}"
    return page(bg, top(bg, n) +
                f"<div class='content'>{eb(bg, e)}<h1 style='font-size:{size}px;color:{t['tx']}'>{h}</h1>{rule(bg)}"
                f"{paras(bg, ps, 35)}"
                f"<div class='card' style='{cs};margin-top:{36 if ps else 0}px'><p style='font-family:Nunito,sans-serif;font-weight:700;font-size:39px;line-height:1.32;color:inherit'>{finding}</p></div>"
                f"{src(bg, s)}</div>" + foot(bg))


def plain(n, bg, e, h, label, text, note=None, size=82):
    """Term in plain language: white card on colour."""
    t = TH[bg]
    nt = f"<p class='lt' style='margin-top:34px;font-size:35px;color:{t['tx']}'>{note}</p>" if note else ''
    return page(bg, top(bg, n) +
                f"<div class='content'>{eb(bg, e)}<h1 style='font-size:{size}px;color:{t['tx']}'>{h}</h1>"
                f"<div class='card' style='background:{WH};margin-top:48px;{'border:3px solid ' + TL if bg in (CR, PY) else ''}'>"
                f"<div class='lab' style='color:{TL}'>{label}</div>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:700;font-size:38px;line-height:1.34;color:{NB}'>{text}</p></div>{nt}</div>" + foot(bg))


def quote(n, bg, e, q, note, send):
    t = TH[bg]
    return page(bg, top(bg, n) +
                f"<div class='content'>{eb(bg, e)}"
                f"<div style='border-left:8px solid {Y if bg in (NB, TL) else TL};padding:6px 0 6px 44px'>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:900;font-style:italic;font-size:58px;line-height:1.2;color:{t['tx']}'>{q}</p></div>"
                f"<p class='lt' style='margin-top:48px;font-size:36px;color:{t['mu'] if bg == NB else t['tx']}'>{note}</p>"
                f"<p style='margin-top:34px;font-family:Nunito,sans-serif;font-weight:900;font-size:28px;color:{Y if bg in (NB, TL) else TL}'>{send}</p></div>" + foot(bg))


def cards(n, bg, e, h, items, note=None, s=None, size=80):
    t = TH[bg]
    li = ''.join(f"<div class='li' style='background:{t['card']}'><i style='background:{t['dot']}'></i><span style='color:{t['ctx']}'>{x}</span></div>" for x in items)
    nt = f"<p class='lt' style='margin-top:24px;font-size:34px;color:{t['tx']}'>{note}</p>" if note else ''
    return page(bg, top(bg, n) +
                f"<div class='content'>{eb(bg, e)}<h1 style='font-size:{size}px;color:{t['tx']};margin-bottom:44px'>{h}</h1>{li}{nt}{src(bg, s)}</div>" + foot(bg))


def agency(n, bg, e, h, ps, small, size=84):
    t = TH[bg]
    return page(bg, top(bg, n) +
                f"<div class='content low'>{eb(bg, e)}<h1 style='font-size:{size}px;color:{t['tx']}'>{h}</h1>{rule(bg)}"
                f"{paras(bg, ps, 37)}"
                f"<p style='margin-top:40px;font-size:29px;font-style:italic;line-height:1.45;color:{t['mu'] if bg != TL else 'rgba(255,255,255,.85)'}'>{small}</p></div>" + foot(bg))


def cta(bg, l1, l2=None, btn='Save this for later', small=None, split=None):
    """Logo, rule, signpost, save button. Split: logo on the top block (Teal), words on the bottom (Cream)."""
    t = TH[bg]
    if split:
        b = TH[split]
        body = (f"<div style='position:absolute;left:0;right:0;top:0;height:55%;display:flex;align-items:center;justify-content:center'>"
                f"<img src='data:image/png;base64,{white_b64}' style='width:440px;display:block;margin-top:40px'></div>"
                f"<div style='position:absolute;left:100px;right:100px;top:55%;bottom:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center'>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:900;font-size:44px;line-height:1.25;color:{b['tx']}'>{l1}</p>"
                + (f"<p style='margin-top:18px;font-size:34px;line-height:1.35;color:{TL};font-weight:500'>{l2}</p>" if l2 else '')
                + (f"<p style='margin-top:26px;font-size:24px;line-height:1.5;color:{WGR}'>{small}</p>" if small else '')
                + (f"<div style='margin-top:34px'><span class='btn' style='background:{TL};color:{WH}'>{btn}</span></div>" if btn else '')
                + "</div>")
        return page(bg, top(bg, 8) + body + foot(split, 'Kew &amp; Croydon, Melbourne'), split=split)
    logo = white_b64 if bg in (NB, TL) else primary_b64
    acc = Y if bg in (NB, TL) else TL
    bs = f"background:{Y};color:{NB}" if bg in (NB, TL) else f"background:{TL};color:{WH}"
    return page(bg, top(bg, 8) +
                f"<div class='content' style='align-items:center;text-align:center'>"
                f"<img src='data:image/png;base64,{logo}' style='width:420px;display:block'>"
                f"<div class='rule' style='width:72px;background:{acc};margin:56px 0 48px'></div>"
                f"<p style='font-family:Nunito,sans-serif;font-weight:900;font-size:46px;line-height:1.25;color:{t['tx']}'>{l1}</p>"
                + (f"<p style='margin-top:18px;font-family:Nunito,sans-serif;font-weight:700;font-size:38px;line-height:1.3;color:{acc}'>{l2}</p>" if l2 else '')
                + (f"<p style='margin-top:40px;font-size:25px;line-height:1.5;color:{t['mu']};max-width:840px'>{small}</p>" if small else '')
                + (f"<div style='margin-top:48px'><span class='btn' style='{bs}'>{btn}</span></div>" if btn else '')
                + "</div>" + foot(bg, 'Kew &amp; Croydon, Melbourne'))


READ = 'Read the full piece at equalpsychology.com.au'
SEND_H = 'Send this to someone who might find it helpful &rarr;'
SEND_N = 'Send this to someone who might need it.'
MG = ("Not sure where to start? The Meet and Greet is a free 15-minute call or in-person meeting, no obligation, "
      "to see if we are the right fit before committing to anything.")

P = {}  # key -> list of html (index 0 = slide 1); None keeps the existing slide

# 23 Oct: ADHD overview (cover butter). PY NB CR Y TL CR NB TL
P['2026-10-23'] = [
    cover(PY, 'ADHD in adults', "Missed, mistaken or misread: <em>four ways</em> the ADHD picture can go wrong",
          "Getting it right is a known challenge in the research. Here is why a careful assessment matters.", 90),
    statement(2, NB, 'Not just too many or too few', "It is not only about over or under diagnosis.",
              ["Research points to errors in both directions, and to a third problem: assuming it has to be one thing or the other."]),
    statement(3, CR, '1. Missed', "ADHD that goes unrecognised for years",
              ["Quieter, mainly inattentive traits and strong coping strategies can hide ADHD, particularly in women and high achievers."],
              s="Source: Attoe &amp; Climie, 2023; AADPA, 2022"),
    research(4, Y, '2. Mistaken for something else', "Recognised as something else first", [],
             "Studies suggest many adults are diagnosed with anxiety, depression or a sleep problem before ADHD is recognised.",
             "Source: Long &amp; Coats, 2022; Okada et al., 2024"),
    statement(5, TL, '3. Something else mistaken for ADHD', "Not everything that looks like ADHD is ADHD",
              ["Poor sleep, thyroid conditions, trauma, and some medicines or stimulants can all affect attention and focus."],
              s="Source: AADPA, 2022; van der Ham et al., 2024", low=True),
    statement(6, CR, '4. Missed alongside', "Both, not either",
              ["ADHD often sits alongside anxiety, depression or autism. Finding one does not rule out another."],
              s="Source: Choi et al., 2022; Hartman et al., 2023", big=True),
    statement(7, NB, 'What Australian guidelines ask for', "More than a questionnaire",
              ["The Australian ADHD guideline says a diagnosis should not rest on rating scales alone.",
               "A careful assessment draws on history back to childhood, health, daily life and other perspectives."],
              s="Source: AADPA, 2022, recommendation 2.1.4"),
    cta(TL, 'Over the coming weeks we unpack each one.', 'Save this and follow along.', btn=None),
]

# 3 Nov: Being less harsh (cover midnight kept). M CR Y TL PY CR NB split(TL/CR)
P['2026-11-03'] = [
    None,
    statement(2, CR, 'The usual advice', "&ldquo;Just be kinder to yourself.&rdquo;",
              ["It assumes harshness and kindness sit on one dial. Turn kindness up, and the critic turns down.",
               "Many people try the kind words anyway. The words feel hollow, and the harsh voice keeps talking underneath."]),
    research(3, Y, 'What the research shows', "The harsh side weighs more",
             ["When research separates the kind and harsh halves of self-compassion, they do not behave like mirror images."],
             "The harsh side is much more closely linked with distress than the kind side is.",
             "Muris &amp; Petrocchi (2017), meta-analysis; Chio et al. (2021), review across many cultures"),
    plain(4, TL, None, "What &ldquo;the harsh side&rdquo; means", 'In plain language',
          "Judging yourself, feeling alone when things go wrong, and getting swept up in painful thoughts.",
          "It is usually fast and familiar. It sounds less like an opinion and more like a fact."),
    quote(5, PY, 'Does this sound familiar?',
          "&ldquo;I have tried saying kind things to myself. It feels fake, and the critic just keeps going.&rdquo;",
          "This is common, and it is not a sign you are bad at self-compassion. You may have been asked to start with the harder job.", SEND_H),
    cards(6, CR, None, "Why kindness can be the harder door",
          ["The harsh voice is automatic. The kind one has to be called up.",
           "For some people, kindness towards themselves feels uncomfortable, even unsafe.",
           "The critic may have felt like the thing keeping you on track.",
           "Worry and rumination can keep the harsh voice looping."],
          note="These overlap, so a small shift in one can make room in the others.", size=74),
    agency(7, NB, 'One thing to notice this week', "Catch the first sentence",
           ["The next time something goes wrong, notice the first sentence your mind produces.",
            "You do not need to change it. Just notice whether it sounds like an observation or a verdict."],
           "Some days it will slip past before you notice. That is part of it."),
    cta(TL, 'Being less harsh may matter more than being kinder', READ, split=CR),
]

# 13 Nov: ADHD lookalikes (cover paper). CR TL Y CR NB PY TL NB
P['2026-11-13'] = [
    cover(CR, 'ADHD in adults', "Not everything that <em>looks like</em> ADHD is ADHD",
          "And sometimes it is ADHD and something else as well."),
    statement(2, TL, 'Why this matters', "Attention is affected by many things",
              ["Focus, memory and restlessness can shift with sleep, health, stress and mood.",
               "Australian guidelines ask clinicians to check for these before, and alongside, an ADHD diagnosis."],
              s="Source: AADPA, 2022"),
    research(3, Y, 'Sleep', "Poor sleep can look a lot like ADHD", [],
             "Short or broken sleep can bring forgetfulness, restlessness and trouble concentrating. Sleep problems are also very common in adults with ADHD.",
             "Source: van der Ham et al., 2024"),
    cards(4, CR, 'Physical health', "Things worth ruling in or out",
          ["Hearing or vision problems", "Thyroid conditions", "Anaemia", "Some medicines, and stimulants such as caffeine"],
          note="These are simple for a GP to check.", s="Source: AADPA, 2022"),
    statement(5, NB, 'Trauma and stress', "Overlap, and often both",
              ["Trauma can affect attention, sleep and emotional control in ways that overlap with ADHD.",
               "The two also commonly occur together, so a careful assessment considers both."],
              s="Source: Magdi et al., 2025", low=True),
    statement(6, PY, 'Mood and substances', "Cause, consequence, or both",
              ["Anxiety, low mood and substance use can all affect focus and motivation.",
               "Australian guidance notes they can also follow from ADHD that went unrecognised."],
              s="Source: AADPA, 2022; Rohner et al., 2023"),
    statement(7, TL, 'Hormones', "An area still being researched",
              ["Hormonal shifts may affect ADHD traits, but research on perimenopause is still early and mixed.",
               "Midlife changes deserve careful, open-minded assessment."],
              s="Source: Osianlis et al., 2025"),
    cta(NB, 'This is why our assessment includes a health and sleep history,',
        'and a letter for your GP about anything worth checking.', btn=None),
]

# 17 Nov: Fear of compassion (cover teal kept). T PY Y NB CR TL CR NB
P['2026-11-17'] = [
    None,
    statement(2, PY, 'A less talked-about experience', "Kindness is supposed to feel good",
              ["For many people it does. For some, it arrives with a tight chest, a joke to deflect it, or a wave of sadness.",
               "Psychologists call this fear of compassion, and it is a recognised pattern in the research."]),
    research(3, Y, 'What the research shows', "The kindness that points at you",
             ["Compassion flows three ways: towards others, from others, and towards yourself. Any of them can be met with fear."],
             "Fear of being kind to yourself, and of receiving kindness, are the fears most closely linked with mental health difficulties.",
             "Kirby et al. (2019), meta-analysis; Gilbert et al. (2011)", size=76),
    plain(4, NB, None, "What &ldquo;fear of compassion&rdquo; means", 'In plain language',
          "A sense that kindness, from others or from yourself, is something to be wary of.",
          "Warmth can reopen old places, including grief for care that was wanted and not received."),
    quote(5, CR, 'Does this sound familiar?',
          "&ldquo;When someone is kind to me, I make a joke or change the subject before it can land.&rdquo;",
          "This is a recognised pattern, not a character flaw. It often made sense once.", SEND_H),
    cards(6, TL, None, "Why it can show up",
          ["Being hard on yourself has felt like it kept you safe", "Kindness can feel undeserved, or like a trap",
           "Warmth can stir up old grief", "Self-compassion can seem weak or self-indulgent"],
          note="Most of these are sensible responses to earlier experience."),
    agency(7, CR, 'One thing to notice this week', "Notice the flinch",
           ["When kindness comes your way, notice what happens in your body before you decide what it means.",
            "A tight chest. A joke. A change of subject. Noticing is enough."],
           "Some days you will brush it away before you notice. That is part of it."),
    cta(NB, 'Why kindness can feel threatening', READ),
]

# 27 Nov: ADHD protocol (cover butter). PY NB Y CR TL PY NB split(TL/CR)
P['2026-11-27'] = [
    cover(PY, 'ADHD assessment', "A careful ADHD assessment looks at <em>the whole picture</em>", "How ours is put together, and why."),
    statement(2, NB, 'Why it takes more than a questionnaire', "Questionnaires are one piece of information",
              ["The Australian ADHD guideline says a diagnosis should not rest on rating scales alone.",
               "Our assessment is built around that guideline."], s="Source: AADPA, 2022, recommendation 2.1.4"),
    research(3, Y, 'Before we meet', "Four questionnaires, one at a time", [],
             "Attention and mood. Sleep and health. Growing up. Daily life, and what it takes to keep it working.",
             "Each one arrives after the last is done, so it never feels like a pile of paperwork."),
    cards(4, CR, 'Two appointments', "What we look at together",
          ["Your childhood and development, with school reports if you have them", "Your health and sleep",
           "How things work day to day, and the effort it takes", "Input from someone who knows you well, if you choose"], size=76),
    statement(5, TL, 'Checking what else is going on', "Looking for the whole picture",
              ["Where our conversation raises a question about autism, mood or substance use, targeted follow-up questionnaires help answer it.",
               "That way the report accounts for it, rather than leaving it open."], low=True),
    cards(6, PY, 'What you receive', "Clear, written, and yours",
          ["A full written report", "A letter for your GP covering anything worth checking",
           "A report written for a psychiatrist, if you want to discuss medication"]),
    statement(7, NB, 'A pathway built in, if you choose', "Psychiatry, already connected",
              ["We developed our psychiatry pathway with Dr Luisa Fernandez of North Psychiatry.",
               "With a GP referral, our report goes to her. She completes the picture with her own assessment and takes on any medical care. Therapy with us stays optional."], size=78),
    cta(TL, 'Adult ADHD assessment', 'Kew, Croydon and online', btn=None, small=MG, split=CR),
]

# 8 Dec: Grief at Christmas (cover paper). CR TL Y PY NB CR TL NB
P['2026-12-08'] = [
    cover(CR, 'Grief at Christmas', "A hard Christmas is <em>not a sign</em> your grief has gone wrong.",
          "What actually separates grief from grief that has become stuck."),
    statement(2, TL, 'Grief at Christmas', "Most of us carry a timetable for grief.",
              ["By the first Christmas, there is a quiet sense that things should be settling.",
               "But how much it hurts on one day tells you very little."]),
    research(3, Y, 'What the research shows', "Meaningful dates bring grief close", [],
             "Among older widowed adults, distress rose around a late partner's birthday and in January after the holidays, in the early months after the loss.",
             "Source: Carr et al., 2014, Journals of Gerontology"),
    plain(4, PY, 'A term worth knowing', "Prolonged grief disorder", 'In plain language',
          "Grief that stays at full intensity for many months, centres on longing for the person, and makes daily life hard to manage. It differs from typical grief in how intense and how long, not in kind.",
          "Most people who grieve never meet this description.", size=80),
    quote(5, NB, 'Does this sound familiar?',
          "&ldquo;Everyone else seems to be moving on. I still reach for the phone to tell her things.&rdquo;",
          "This is a recognised part of grief. It is not a sign something is wrong with you.", SEND_N),
    cards(6, CR, 'It is not just one thing', "What can make grief heavier",
          ["Grief or low mood before the loss", "An unexpected death", "A violent death", "Losing a partner or a child"],
          note="This is not a forecast. It is a reason to be gentle with the pace."),
    agency(7, TL, 'One thing to try this week', "Notice the shape, not the size.",
           ["This week, notice whether the longing comes in waves around certain days, or stays at the same pitch most of the time."],
           "Hard days are part of grief, not a step backwards."),
    cta(NB, READ.replace(' at ', ' at<br>')),
]

# 16 Dec: Making room for grief (cover midnight). NB PY Y TL CR NB PY TL
P['2026-12-16'] = [
    cover(NB, 'Grief at Christmas', "Grief does not take <em>the holidays off.</em>",
          "Making room for grief at Christmas, for yourself and for the people you love.", 100),
    statement(2, PY, 'Grief at Christmas', "The holidays are built from memory.",
              ["The seat that was always theirs. The voice that started the same song.",
               "When someone is missing, the season places you back inside those moments."]),
    research(3, Y, 'What the research shows', "Rituals keep us connected", [],
             "Across many cultures, rituals may help people keep a continuing bond with the person who died, and may strengthen ties between those who are left.",
             "Source: Killikelly et al., 2025, The Lancet"),
    plain(4, TL, 'A term worth knowing', "Continuing bond", 'In plain language',
          "A way of staying connected to the person who died, through rituals, stories and small acts of remembering.",
          "The connection does not end. It changes shape."),
    quote(5, CR, 'Does this sound familiar?',
          "&ldquo;I don&rsquo;t know whether to keep our traditions or skip Christmas altogether this year.&rdquo;",
          "There is no right answer. Both are ways of loving someone who is no longer in the room.", SEND_N),
    cards(6, NB, 'Small, not grand', "Ways to make room",
          ["A candle lit at the start of the meal", "Their name said out loud",
           "A favourite dish cooked in their honour", "A little company planned for January too"],
          note="Choose what fits. Leave what does not."),
    agency(7, PY, 'One thing to try this week', "Check in with yourself, the way you would with a friend.",
           ["Ask: how am I going right now, and what do I need in the next hour?"],
           "Some days will be harder than others. That is part of it.", size=80),
    cta(TL, READ.replace(' at ', ' at<br>')),
]

# Singles
S = {
    '2026-10-24': single(NB, 'Chronic stress', "Stress does not just feel bad. It quietly <em>turns down</em> the part of your brain you think with.",
                         "That is why fog, forgetfulness and low mood arrive together. They come from the same overloaded system, and they tend to ease as the load comes down.", 86),
    '2026-10-28': single(CR, 'Meaning in your 20s', "Searching for meaning is not the problem. Searching without <em>a sense of control</em> is.",
                         "The questioning is human and healthy. It only tips into distress when it comes with the feeling that your choices do not count.", 92),
    '2026-12-12': single(TL, 'Grief at Christmas', "The question is not whether it still hurts. It is whether it is <em>still moving.</em>",
                         "Intensity on one day tells you little. What matters is the shape of grief across months.", 96),
    '2026-12-20': single(TL, 'Grief at Christmas', "Grief at Christmas is not a problem to fix. It is part of <em>still loving someone.</em>",
                         "It does not need a solution. It needs a little room at the table.", 88, split=CR),
}

for d, slides in P.items():
    for i, h in enumerate(slides, 1):
        if h:
            open(f'{OUT}/C_{d}_{i}.html', 'w').write(h)
for d, h in S.items():
    open(f'{OUT}/S_{d}.html', 'w').write(h)
print('ok')
