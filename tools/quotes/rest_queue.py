"""Write the four Worth sending queue files (pending_review) and copy media into the social-media repo."""
import json, os, re, shutil, glob
R = '/home/claude/social-media'
RAW = 'https://raw.githubusercontent.com/EqualPsych/social-media/main/'
Q = '/home/claude/ig/quotes'
DIS = ("This content is for general informational purposes and does not constitute psychological advice. "
       "If you are experiencing significant distress, please speak with a registered health professional.")
SER = "Worth sending is our new series: one short line, for the person who needs to hear it."
AG = "Agolli, A., & Holtz, B. C. (2023). Facilitating detachment from work: A systematic review, evidence-based recommendations, and guide for future research. Journal of Occupational Health Psychology, 28(3), 129-159. https://doi.org/10.1037/ocp0000353"
KA = "Karabinski, T., Haun, V. C., Nübold, A., Wendsche, J., & Wegge, J. (2021). Interventions for improving psychological detachment from work: A meta-analysis. Journal of Occupational Health Psychology, 26(3), 224-242. https://doi.org/10.1037/ocp0000280"
GR = "Grant, R. S., Buchanan, B. E., & Shockley, K. M. (2025). I need a vacation: A meta-analysis of vacation and employee well-being. Journal of Applied Psychology. https://doi.org/10.1037/apl0001262"
NOTE = "These were studies of working adults in general, not people with burnout. And if the workload itself is too much, that sits with the workplace too."

POSTS = {
 '2026-12-01': dict(format='single', cover='receipt (sunshine)', slug='worth-sending-receipt', png='S_2026-12-01-receipt.png',
   topic='Worth sending 01: You don\'t have to earn a rest (receipt single, quote series experiment)',
   caption=f"""Rest isn't a prize for finishing everything.

In studies of working adults, mentally switching off from work while away was one of the things most linked with feeling better after a holiday. That's a link, not proof of cause. Waiting until everything is done can mean the break never really starts.

Send this to someone who hasn't stopped all year.

{SER} {NOTE}

Research:
{GR}

{DIS}

#equalpsychology #rest #burnout #worklifebalance #mentalhealth"""),
 '2026-12-02': dict(format='reel', cover='lock screen (teal)', slug='worth-sending-not-tonight', mp4='reels/2026-12-02-not-tonight.mp4', music='warmkeys',
   topic='Worth sending 02: Not every message needs an answer tonight (lock-screen Reel, music only, quote series experiment)',
   caption=f"""10:47pm and the work messages are still coming in?

Researchers call switching off from work in your own time psychological detachment. A review of workplace programs found the ones that worked better often built a clear boundary between work and home, including putting work messages away.

Send this to someone still answering emails at 10pm.

{SER} {NOTE}

Research:
{AG}

{DIS}

#equalpsychology #worklifebalance #workstress #switchoff #mentalhealth"""),
 '2026-12-03': dict(format='single', cover='light switch (paper)', slug='worth-sending-off-means-off', png='S_2026-12-03-switch.png',
   topic='Worth sending 03: Off means off (light-switch single, quote series experiment)',
   caption=f"""On leave, but still checking in "just in case"?

Switching off from work in your own time can be learnt. A review of programs for working adults found they helped people do it, on average. The most helpful ones worked on boundaries between work and home.

Send this to someone about to start their leave.

{SER} {NOTE}

Research:
{KA}

{DIS}

#equalpsychology #rest #worklifebalance #holidays #mentalhealth"""),
 '2026-12-04': dict(format='reel', cover='out-of-office (butter)', slug='worth-sending-logging-off', mp4='reels/2026-12-04-logging-off.mp4', music='guitar',
   topic='Worth sending 04: Logging off is part of the job (out-of-office Reel, music only, quote series experiment)',
   caption=f"""Logging off can feel like letting people down. It's part of doing the job well.

A review of workplace programs found that simple end-of-day habits can help people switch off: planning unfinished tasks, noting what went well, and putting work messages away.

Send this to the colleague who never logs off.

{SER} {NOTE}

Research:
{AG}

{DIS}

#equalpsychology #worklifebalance #workstress #burnout #mentalhealth"""),
}

for d, p in POSTS.items():
    c = p['caption']
    first = re.split(r'(?<=[.?!])\s', c, maxsplit=1)[0]
    bad = [ch for ch in c if ch in '—–​‌‍⁠­﻿  ']
    assert len(first) <= 125 and not bad and len(re.findall(r'#\w+', c)) <= 5 and len(c) < 2200 and 'specialis' not in c.lower(), d
    out = dict(date=d, platform='instagram', account='@equal_psychology', status='pending_review', format=p['format'],
               cover=p['cover'], goal='share', topic=p['topic'])
    if p['format'] == 'single':
        folder = f'instagram/2026-12/{d}-{p["slug"]}'
        os.makedirs(f'{R}/{folder}', exist_ok=True)
        shutil.copy(f'{Q}/objpng/{p["png"]}', f'{R}/{folder}/post.png')
        out['media'] = [RAW + folder + '/post.png']
    else:
        path = f'instagram/reels/{d}-{p["slug"]}.mp4'
        shutil.copy(f'{Q}/{p["mp4"]}', f'{R}/{path}')
        out.update(video=RAW + path, voice=None, music=p['music'])
    out.update(experiment='quote-series',
               experiment_note='Worth sending: one-line quote drawn as an everyday object, research in the caption. Judge on sends and follows per view against our usual singles and Reels. Four posts cannot settle anything.',
               caption=c, build_note='Built 23 Nov 2026 (tools: ig/quotes/build_objects.py). Sources reused from verified Nov 2026 and Jan 2027 posts.')
    f = f'{R}/instagram-queue/{d}.json'
    assert not os.path.exists(f), f'{d} taken'
    json.dump(out, open(f, 'w'), indent=2, ensure_ascii=False)
    print(d, len(c), len(first))
