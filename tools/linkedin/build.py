import base64, os, html
ROOT = '/home/claude/ig'
OUT = f'{ROOT}/li/html'
os.makedirs(OUT, exist_ok=True)

def font(pkg, fam, w):
    p = f'{ROOT}/node_modules/@fontsource/{pkg}/files/{pkg}-latin-{w}-normal.woff2'
    return (f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,"
            f"{base64.b64encode(open(p,'rb').read()).decode()}) format('woff2');}}")
FONTS = ''.join([font('nunito','Nunito',w) for w in (700,800,900)] + [font('roboto','Roboto',w) for w in (300,400,500)])
LOGO = {'white': open(f'{ROOT}/logo_white_b64.txt').read().strip(),
        'primary': open(f'{ROOT}/logo_yellow_b64.txt').read().strip()}

Y, PY, CR, NB, TL, WG, WH, DG = '#F2BE1A', '#FFF6E0', '#F7F5EB', '#1A1A1A', '#2A7469', '#6E6862', '#FFFFFF', '#7A5C00'

THEMES = {
  # bg, text, muted, eyebrow, logo, stripe, card bg, card text, accent (dots/labels), callout style
  'teal':   dict(bg=TL, fg=WH, mute=WH, eye=PY, logo='white', stripe=Y, card=WH, ctext=NB, acc=TL, lab=TL, hl='dark'),
  'cream':  dict(bg=CR, fg=NB, mute=WG, eye=TL, logo='primary', stripe=TL, card=WH, ctext=NB, acc=TL, lab=TL, hl='light'),
  'butter': dict(bg=PY, fg=NB, mute=WG, eye=DG, logo='primary', stripe=Y, card=WH, ctext=NB, acc=TL, lab=DG, hl='light'),
  'white':  dict(bg=WH, fg=NB, mute=WG, eye=TL, logo='primary', stripe=Y, card=CR, ctext=NB, acc=TL, lab=TL, hl='light'),
}

def hl(text, t):
    # one call-out: *word* -> highlighted
    if '*' not in text: return html.escape(text)
    a, b, c = text.split('*')
    if t['hl'] == 'dark':
        em = f"<em style='font-style:normal;color:{Y}'>{html.escape(b)}</em>"
    else:
        em = (f"<em style='font-style:normal;background:linear-gradient(transparent 58%,{Y} 58%,{Y} 92%,transparent 92%)'>"
              f"{html.escape(b)}</em>")
    return html.escape(a) + em + html.escape(c)

def css(t):
    return FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1160px;height:1430px;background:#f00;display:flex;align-items:center;justify-content:center;-webkit-font-smoothing:antialiased}}
.slide{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{t['bg']};color:{t['fg']};font-family:'Roboto',sans-serif}}
.stripe{{position:absolute;top:0;left:0;right:0;height:8px;background:{t['stripe']}}}
.top{{position:absolute;top:72px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:center}}
.top img{{height:88px}}
.eye{{font-family:'Nunito';font-weight:800;font-size:23px;letter-spacing:.12em;text-transform:uppercase;color:{t['eye']}}}
.content{{position:absolute;left:88px;right:88px;top:210px;bottom:150px;display:flex;flex-direction:column;justify-content:center;gap:34px}}
.pill{{align-self:flex-start;font-family:'Nunito';font-weight:900;font-size:21px;letter-spacing:.1em;text-transform:uppercase;padding:11px 24px;border-radius:999px;background:{Y if t['hl']=='light' else PY};color:{NB}}}
h1{{font-family:'Nunito';font-weight:900;font-size:66px;line-height:1.08;letter-spacing:-.02em;text-wrap:balance}}
.lab{{font-family:'Nunito';font-weight:800;font-size:21px;letter-spacing:.1em;text-transform:uppercase;color:{t['lab']};margin-bottom:12px}}
.card{{background:{t['card']};color:{t['ctext']};border-radius:20px;padding:30px 34px}}
.list{{display:flex;flex-direction:column;gap:0}}
.row{{display:flex;gap:20px;align-items:flex-start;padding:15px 0;border-top:1.5px solid rgba(110,104,98,.25);font-size:29px;line-height:1.35}}
.row:first-of-type{{border-top:none;padding-top:4px}}
.dot{{flex:0 0 14px;height:14px;border-radius:50%;background:{t['acc']};margin-top:13px}}
.num{{flex:0 0 44px;height:44px;border-radius:50%;background:{t['acc']};color:{WH};font-family:'Nunito';font-weight:900;font-size:23px;display:flex;align-items:center;justify-content:center}}
.row b{{font-weight:500}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.chips{{display:flex;flex-wrap:wrap;gap:12px}}
.chip{{font-family:'Nunito';font-weight:800;font-size:28px;padding:12px 24px;border-radius:999px;border:2.5px solid {t['acc']};color:{t['ctext']}}}
.q{{font-family:'Nunito';font-weight:800;font-size:34px;line-height:1.3;padding-left:26px;border-left:7px solid {Y}}}
.qlab{{font-family:'Nunito';font-weight:800;font-size:21px;letter-spacing:.1em;text-transform:uppercase;color:{t['eye']};margin-bottom:12px}}
.line{{font-size:30px;line-height:1.4;font-weight:400;text-wrap:pretty}}
.note{{font-size:23px;line-height:1.4;color:{t['mute']};{'opacity:.85;' if t['hl']=='dark' else ''}}}
.foot{{position:absolute;bottom:64px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:flex-end;gap:30px;font-size:22px}}
.src{{color:{t['mute']};{'opacity:.85;' if t['hl']=='dark' else ''}line-height:1.35;max-width:640px}}
.site{{font-weight:500;white-space:nowrap}}
th,td{{text-align:left;vertical-align:top}}
.tbl{{border-radius:20px;overflow:hidden;background:{t['card']};color:{t['ctext']}}}
.tbl .h{{display:grid;grid-template-columns:1fr 1fr}}
.tbl .h div{{font-family:'Nunito';font-weight:900;font-size:25px;padding:22px 28px}}
.tbl .r{{display:grid;grid-template-columns:1fr 1fr;border-top:1.5px solid rgba(110,104,98,.2)}}
.tbl .r div{{font-size:27px;line-height:1.35;padding:22px 28px}}
.tbl .r div:first-child{{color:{WG}}}
.tbl .r div:last-child{{font-weight:500;border-left:1.5px solid rgba(110,104,98,.2)}}
"""

def page(name, theme, blocks, sources):
    t = THEMES[theme]
    body = ''
    for kind, *a in blocks:
        if kind == 'pill': body += f"<div class='pill'>{html.escape(a[0])}</div>"
        elif kind == 'h1': body += f"<h1>{hl(a[0], t)}</h1>"
        elif kind == 'list':
            lab, items, style = a[0], a[1], (a[2] if len(a) > 2 else 'dot')
            rows = ''.join(f"<div class='row'>{'<div class=dot></div>' if style=='dot' else f'<div class=num>{i+1}</div>'}<div>{x}</div></div>" for i, x in enumerate(items))
            body += f"<div class='card'>{f'<div class=lab>{lab}</div>' if lab else ''}<div class='list'>{rows}</div></div>"
        elif kind == 'chips':
            lab, items = a
            body += f"<div class='card'><div class='lab'>{lab}</div><div class='chips'>{''.join(f'<div class=chip>{html.escape(x)}</div>' for x in items)}</div></div>"
        elif kind == 'table':
            h1_, h2_, rows = a
            body += (f"<div class='tbl'><div class='h'><div style='background:{CR};color:{NB}'>{h1_}</div>"
                     f"<div style='background:{Y};color:{NB}'>{h2_}</div></div>"
                     + ''.join(f"<div class='r'><div>{l}</div><div>{r}</div></div>" for l, r in rows) + "</div>")
        elif kind == 'q': body += f"<div><div class='qlab'>{a[0]}</div><div class='q'>{html.escape(a[1])}</div></div>"
        elif kind == 'line': body += f"<div class='line'>{a[0]}</div>"
        elif kind == 'note': body += f"<div class='note'>{a[0]}</div>"
    doc = (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><style>{css(t)}</style></head><body><div class='slide'>"
           f"<div class='stripe'></div><div class='top'><img src='data:image/png;base64,{LOGO[t['logo']]}'><div class='eye'>Research for practice</div></div>"
           f"<div class='content'>{body}</div>"
           f"<div class='foot'><div class='src'>{html.escape(sources)}</div><div class='site'>equalpsychology.com.au</div></div>"
           f"</div></body></html>")
    open(f'{OUT}/{name}.html', 'w').write(doc)

# ---------------- posts (wording taken from each approved post) ----------------
page('2026-10-29-emotion-regulation', 'teal', [
  ('pill', 'Emotion regulation'),
  ('h1', 'Emotion regulation may be a *shared thread* across diagnoses'),
  ('list', 'A 2026 meta-analysis of 188 studies found that adults living with a condition reported', [
     'More difficulty regulating their emotions',
     'Rethinking situations less often',
     'Holding back the outward expression of feelings more often']),
  ('q', 'Within your role, ask with curiosity', 'How do you usually handle strong feelings?'),
  ('note', 'Self-report and mostly cross-sectional studies, in adults only.'),
], 'Source: Sloan et al., 2026')

page('2026-11-02-in-practice-10', 'butter', [
  ('pill', 'In Practice, issue 10'),
  ('h1', 'Being less harsh is not the same as *being kinder*'),
  ('list', 'What the issue covers', [
     '<b>Two levers, not one.</b> The harsh side of self-compassion sits closer to distress',
     '<b>When kindness feels threatening</b> particularly for people who are highly self-critical',
     '<b>Self-criticism is changeable</b>',
     '<b>Three consult questions</b> and when to consider a referral'], 'num'),
  ('line', 'Free issue and patient handout on our referrers page.'),
], 'Sources: Muris & Petrocchi, 2017; Kirby et al., 2019; Chio et al., 2021; Wakelin et al., 2022')

page('2026-11-05-safety-behaviours', 'cream', [
  ('pill', 'Anxiety'),
  ('h1', 'The small things people do to feel safe *may keep fear going*'),
  ('chips', 'Safety behaviours, for example', ['Mirror checking', 'Avoiding eye contact', 'Searching symptoms online']),
  ('list', 'A 2026 review of 26 studies found', [
     'Cutting back on these behaviours was linked with fewer symptoms than control conditions']),
  ('q', 'Get curious rather than correcting', 'What do you worry might happen if you did not do that?'),
], 'Source: Goodson et al., 2026')

page('2026-11-10-self-criticism', 'white', [
  ('pill', 'Self-criticism'),
  ('h1', 'Self-compassion bundles *two different things*'),
  ('table', 'Easing harshness', 'Building warmth', [
     ('Self-judgement, isolation, getting swept up in failures', 'Turning towards yourself with warmth'),
     ('More closely linked to distress', 'Mattered more for wellbeing')]),
  ('line', 'For some people who are most self-critical, kindness itself can feel threatening. If "be kinder to yourself" meets resistance, that response is information.'),
  ('note', 'Mostly associations, not cause and effect.'),
], 'Sources: Gilbert et al., 2011; Muris & Petrocchi, 2017; Kirby et al., 2019; Chio et al., 2021; Wakelin et al., 2022')

page('2026-11-12-self-compassion-views', 'teal', [
  ('pill', 'Self-compassion'),
  ('h1', 'Resisting self-kindness may be a *belief*, not low motivation'),
  ('chips', 'Before starting, some participants saw self-compassion as', ['Self-indulgent', 'Weak', 'Lazy']),
  ('q', 'A question that opens the conversation', 'What would it mean about you if you went easier on yourself?'),
  ('note', 'A review of 12 qualitative studies of compassion-focused therapy. They describe experiences rather than measure outcomes.'),
], 'Source: Garrett, Smith & Wittkowski, 2025')

page('2026-11-17-perimenopause', 'butter', [
  ('pill', 'Perimenopause'),
  ('h1', 'Mental health changes can begin in *perimenopause*'),
  ('table', 'Common assumption', 'What the evidence points to', [
     ('The mental health side of menopause comes later, after the hot flushes', 'Mood, anxiety and cognitive changes can arrive years before hot flushes'),
     ('It is mostly about falling oestrogen', 'How unpredictably oestrogen fluctuates appears to matter')]),
  ('line', 'Midlife brain fog is common and, in almost all cases, is not an early sign of dementia.'),
  ('q', 'Whatever your role', 'Ask gently and directly, and ask about sleep alongside mood.'),
], 'Sources: Davis et al., 2023; Badawy et al., 2024')

page('2026-11-19-insomnia', 'cream', [
  ('pill', 'Insomnia'),
  ('h1', 'CBTi, not sleep hygiene alone, is *first line* for adult insomnia'),
  ('list', 'A joint position statement from six Australian organisations', [
     'Australasian Sleep Association · Sleep Health Foundation · RACGP',
     'Australian Psychological Society · Pharmaceutical Society of Australia · Australian Primary Health Care Nurses Association']),
  ('line', 'General sleep hygiene advice is not a sufficient stand alone treatment for chronic insomnia.'),
  ('q', 'When someone says they have had help with sleep', 'What did that help involve?'),
], 'Source: Sweetman et al., 2026')

page('2026-11-26-loneliness', 'white', [
  ('pill', 'Loneliness'),
  ('h1', 'Loneliness can arise even when someone is *not isolated*'),
  ('list', 'Cognitive behavioural approaches had the most consistent evidence. They focused on', [
     'Reappraising unhelpful thoughts about loneliness',
     'Easing avoidance',
     'Building coping skills and engaging socially']),
  ('q', 'Listen for beliefs about connection', 'What tends to stop you reaching out?'),
  ('note', 'A review of 22 randomised trials, each judged to carry some or high risk of bias.'),
], 'Source: Birken et al., 2026')

page('2026-12-01-in-practice-11', 'teal', [
  ('pill', 'In Practice, issue 11'),
  ('h1', 'A hard first Christmas can be *typical grief*'),
  ('list', 'What the issue covers', [
     '<b>Special dates can sharpen grief</b>, mainly in the first months after a loss',
     '<b>Prolonged grief disorder</b> differs in intensity and duration, not in kind',
     '<b>Who benefits from formal support</b>',
     '<b>Three consult questions</b> and when to consider a referral'], 'num'),
  ('line', 'Free issue and patient handout on our referrers page. Lifeline: <span style="white-space:nowrap">13 11 14</span>.'),
], 'Sources: Carr et al., 2014; Aoun et al., 2018; Avis et al., 2025; Killikelly et al., 2025')
print('built')
