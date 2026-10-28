#!/usr/bin/env python3
"""Build reports/social/dashboard.json for the website's admin Social page (/admin/social).

One file that holds every scheduled and posted item from the three queues (Instagram, its Facebook mirror, LinkedIn,
Google Business Profile), with status, format, test variables and the interaction counts recorded by the weekly tracking
task (reports/social/interactions.json), plus follower history and weekly Google Business figures.

Runs automatically on every push to main (.github/workflows/build-dashboard.yml). It can also be run by hand:
    python3 scripts/build_dashboard.py
Text of posts is not copied in full: only the first line (the hook) is kept, so the dashboard stays small.
"""
import glob
import json
import os
import re
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = 'https://raw.githubusercontent.com/EqualPsych/social-media/main/'
SERIES = [("Your brain's best guess", "Your brain's best guess"), ('ADHD: the full picture', 'ADHD: the full picture'),
          ('ADHD misdiagnosis', 'ADHD: the full picture')]


def load(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return json.load(f)


def first_line(s, n=160):
    s = (s or '').strip().split('\n')[0].strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def thumb_for(d):
    """A small picture for the calendar: first carousel image, the post image, or a poster frame made for a video."""
    if d.get('media'):
        return d['media'][0]
    if d.get('image_url'):
        return d['image_url']
    v = d.get('video')
    if v and v.startswith(RAW):
        poster = v[len(RAW):].rsplit('.', 1)[0] + '.thumb.jpg'
        if os.path.exists(os.path.join(ROOT, poster)):
            return RAW + poster
    return None


def series_of(topic):
    for needle, name in SERIES:
        if (topic or '').startswith(needle):
            return name
    return None


def kind_of(d):
    """The content type used for comparisons."""
    f = (d.get('format') or '').lower()
    if f == 'reel':
        if d.get('companion_of'):
            return 'Companion Reel'
        return 'Reel (video background)' if d.get('experiment') == 'video-background' else 'Reel'
    return {'carousel': 'Carousel', 'single': 'Single image'}.get(f, (d.get('format') or 'Post').capitalize())


def follower_history(inter):
    """One list of follower totals by date, from every place they are recorded: the weekly Meta workflow and the
    monthly report (interactions.json), the Instagram snapshots (reports/instagram/history.json) and the LinkedIn
    analytics exports (reports/linkedin/history.json). A value already recorded for a date and platform is kept."""
    by = {}

    def put(ds, platform, n):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(ds or '')) or not isinstance(n, int) or n < 0:
            return
        by.setdefault(ds, {'date': ds}).setdefault(platform, n)

    for r in inter.get('followers', []):
        for k in ('instagram', 'facebook', 'linkedin'):
            put(r.get('date'), k, r.get(k))
    for path, key, field in (('reports/instagram/history.json', 'instagram', 'followers'), ('reports/linkedin/history.json', 'linkedin', 'total')):
        if os.path.exists(os.path.join(ROOT, path)):
            d = load(path)
            rows = [r for k in ('snapshots', 'followers') if isinstance(d.get(k), list) for r in d[k]]
            for r in rows:
                if isinstance(r, dict):
                    put(r.get('date'), key, r.get(field))
    return [by[k] for k in sorted(by)]


def weekday(ds):
    return date.fromisoformat(ds).strftime('%A')


def main():
    inter = load('reports/social/interactions.json') if os.path.exists(os.path.join(ROOT, 'reports/social/interactions.json')) else {'posts': [], 'followers': []}
    gbp = load('reports/social/gbp.json') if os.path.exists(os.path.join(ROOT, 'reports/social/gbp.json')) else {'weeks': []}
    by = {}
    for r in inter.get('posts', []):
        by.setdefault((r['platform'], r['date']), []).append(r)

    def counts(platform, ds, pid=None):
        rows = by.get((platform, ds), [])
        if pid:
            rows = [r for r in rows if not r.get('id') or str(r.get('id')) == str(pid)] or rows
        if not rows:
            return None
        r = rows[0]
        return {k: r[k] for k in ('latest', 'day7', 'url') if k in r}

    posts = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'instagram-queue', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        ds = d['date']
        topic = d.get('topic') or ''
        base = {
            'date': ds, 'weekday': weekday(ds), 'topic': topic, 'hook': first_line(d.get('caption')),
            'format': d.get('format'), 'kind': kind_of(d), 'series': series_of(topic), 'cover': d.get('cover'),
            'voice': d.get('voice'), 'music': d.get('music'), 'slot': d.get('slot') or 'morning',
            'companion_of': d.get('companion_of'), 'experiment': d.get('experiment'), 'experiment_note': d.get('experiment_note'),
            'blog_url': d.get('blog_url'), 'facebook_mirror': d.get('facebook_mirror'), 'thumb': thumb_for(d), 'source': 'instagram-queue/' + os.path.basename(f),
        }
        pid = None
        if d.get('posted_url'):
            m = re.search(r'(\d{12,})', str(d['posted_url']))
            pid = m.group(1) if m else None
        posts.append({**base, 'platform': 'instagram', 'status': d.get('status'), 'posted_at': d.get('posted_at'),
                      'url': d.get('posted_url') if str(d.get('posted_url', '')).startswith('http') else (counts('instagram', ds, pid) or {}).get('url'),
                      'held_reason': d.get('held_reason'), 'interactions': counts('instagram', ds, pid)})
        if d.get('facebook_mirror') is False:
            continue
        fb = d.get('facebook') or {}
        if not fb and d.get('status') not in ('approved', 'pending_review', 'held'):
            continue   # posted before the Facebook mirror started (15 Oct 2026), or never mirrored
        fb_status = fb.get('status') or ('held' if d.get('status') == 'held' else d.get('status'))
        if fb_status == 'posted' or d.get('status') in ('approved', 'pending_review', 'held') or fb:
            fb_url = fb.get('id_or_url')
            if re.fullmatch(r'\d+_\d+', str(fb_url or '')):
                fb_url = 'https://www.facebook.com/' + fb_url   # Meta route records the post id
            if not str(fb_url or '').startswith('http'):
                fb_url = (counts('facebook', ds) or {}).get('url')
            posts.append({**base, 'platform': 'facebook', 'status': fb_status, 'posted_at': fb.get('posted_at'), 'url': fb_url,
                          'held_reason': d.get('held_reason') or fb.get('error'), 'interactions': counts('facebook', ds)})

    for f in sorted(glob.glob(os.path.join(ROOT, 'linkedin-queue', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        ds = d['date']
        m = re.search(r'urn:li:share:\d+', str(d.get('posted_url') or ''))
        posts.append({'platform': 'linkedin', 'date': ds, 'weekday': weekday(ds), 'topic': d.get('topic'), 'hook': first_line(d.get('text')),
                      'format': d.get('format'), 'kind': (d.get('format') or 'post').capitalize(), 'slot': d.get('slot') or 'morning',
                      'status': d.get('status'), 'posted_at': d.get('posted_at'), 'url': d.get('posted_url'), 'thumb': d.get('image_url'),
                      'held_reason': d.get('held_reason'), 'source': 'linkedin-queue/' + os.path.basename(f),
                      'interactions': counts('linkedin', ds, m.group(0) if m else None)})

    for f in sorted(glob.glob(os.path.join(ROOT, 'gbp-queue', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        ds = d['date']
        results = {k: v.get('status') for k, v in (d.get('results') or {}).items() if isinstance(v, dict)}
        posts.append({'platform': 'gbp', 'date': ds, 'weekday': weekday(ds), 'topic': d.get('topic'), 'hook': first_line(d.get('summary')),
                      'format': 'Google post', 'kind': 'Google post', 'slot': d.get('slot') or 'morning', 'status': d.get('status'),
                      'locations': results, 'url': d.get('cta_url'), 'thumb': d.get('image_url'), 'blog_url': d.get('blog_url'),
                      'held_reason': d.get('held_reason'), 'source': 'gbp-queue/' + os.path.basename(f), 'interactions': None})

    posts.sort(key=lambda p: (p['date'], ['instagram', 'facebook', 'linkedin', 'gbp'].index(p['platform'])))
    out = {
        'generated': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'note': 'Built by scripts/build_dashboard.py from the queues and reports/social. Read by equalpsychology.com.au/admin/social.',
        'followers': follower_history(inter),
        'unavailable': ['Instagram reach, saves and shares (the Instagram connection has no insights permission)',
                        'LinkedIn impressions', 'Google Business figures per post (Google gives whole-profile numbers only)'],
        'posts': posts,
        'gbp_weeks': gbp.get('weeks', []),
    }
    path = os.path.join(ROOT, 'reports/social/dashboard.json')
    old = None
    if os.path.exists(path):
        old = json.load(open(path, encoding='utf-8'))
        old.pop('generated', None)
    cmp = dict(out)
    cmp.pop('generated')
    if old == cmp:
        print('dashboard.json unchanged')
        return
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'dashboard.json written: {len(posts)} items')


if __name__ == '__main__':
    main()
