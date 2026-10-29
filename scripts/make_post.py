#!/usr/bin/env python3
"""Post a LinkedIn or Google Business Profile queue file through the Make scenario (free plan), and record the result.

Runs from .github/workflows/make-post.yml. Two ways in:
- Scheduled (8:22am Melbourne): posts today's approved LinkedIn and Google Business files, but only for platforms that
  posting.json routes to "make". While they are still routed to "zapier", the scheduled run does nothing, so the two
  routes never both post.
- "Post now" from the admin Social tab: the website starts this workflow with --date and --platform. That posts the
  named approved file whatever posting.json says. The Zapier task skips files already marked "posted".

The Make scenario "EP social posting (LinkedIn and Google Business)" (team 1872999, scenario 8244876) receives a JSON
body on its webhook and replies in plain text:
    POSTED linkedin urn:li:share:123
    POSTED gbp Kew accounts/.../localPosts/...      (one line per location)
    FAILED <platform/location>: <error>              (HTTP 502)
Its webhook address is the repository secret MAKE_POST_WEBHOOK. It is never printed.

Rules match the Claude posting task: only "approved" files; text published exactly as written apart from link tags
on equalpsychology.com.au links; Google Business posts wait for their blog to be live; a location already posted is
never posted again.

    python3 scripts/make_post.py                               # scheduled run (today, morning window)
    python3 scripts/make_post.py --date 2026-11-05 --platform linkedin
"""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEL = ZoneInfo('Australia/Melbourne')
HOOK = os.environ.get('MAKE_POST_WEBHOOK', '').strip()
QUEUE = {'linkedin': 'linkedin-queue', 'gbp': 'gbp-queue'}
LOCATIONS = ('Kew', 'Croydon')   # the scenario posts to both, Kew first


def git(*a):
    return subprocess.run(['git', '-C', ROOT, *a], check=True, capture_output=True, text=True).stdout.strip()


def push():
    for _ in range(3):
        try:
            git('pull', '--rebase', '-q')
            git('push', '-q')
            return
        except subprocess.CalledProcessError:
            time.sleep(5)
    raise RuntimeError('could not push')


def now_iso():
    return datetime.now(MEL).isoformat(timespec='seconds')


def tag(url, src, medium, date):
    """Link tag so website visits from the post are counted (same rule as the Claude posting task)."""
    if not url.startswith('https://equalpsychology.com.au'):
        return url
    frag = ''
    if '#' in url:
        url, frag = url.split('#', 1)
        frag = '#' + frag
    sep = '&' if '?' in url else '?'
    return f'{url}{sep}utm_source={src}&utm_medium={medium}&utm_campaign=post-{date}{frag}'


def tag_links(text, src, medium, date):
    return re.sub(r'https://equalpsychology\.com\.au[^\s)\]]*', lambda m: tag(m.group(0), src, medium, date), text)


# LinkedIn's posts API reads "little text format": these characters must be escaped or the post is cut short at the
# first one (Zapier did this for us with allow_reserved_characters false). Hashtags are written as hashtag elements
# so they stay clickable.
RESERVED = set('\\|{}@[]()<>#*_~')


def little_text(text):
    out, i = [], 0
    while i < len(text):
        m = re.match(r'#([A-Za-z][A-Za-z0-9]*)', text[i:])
        if m and (i == 0 or text[i - 1].isspace()):
            # A hashtag. A '#' straight after other characters (a link such as /referrers#in-practice) is escaped instead.
            out.append('{hashtag|\\#|' + m.group(1) + '}')
            i += len(m.group(0))
            continue
        out.append('\\' + text[i] if text[i] in RESERVED else text[i])
        i += 1
    return ''.join(out)


def blog_live(url):
    try:
        req = urllib.request.Request(url, headers={'user-agent': 'Mozilla/5.0 (EqualPsych social poster)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(200000).decode('utf-8', 'ignore').lower()
            return r.status == 200 and 'page not found' not in body[:20000]
    except Exception:
        return False


def call_make(payload):
    """POST the payload to the scenario. Returns (ok, lines). The webhook address is never printed."""
    req = urllib.request.Request(HOOK, data=json.dumps(payload).encode(), method='POST',
                                 headers={'content-type': 'application/json', 'user-agent': 'EqualPsych social poster'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            body = r.read().decode('utf-8', 'ignore').strip()
            return r.status == 200, body.splitlines()
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'ignore').strip()
        return False, (body or f'HTTP {e.code}').splitlines()
    except Exception as e:
        return False, [f'Could not reach Make: {type(e).__name__}']


def post_linkedin(d, date):
    text = little_text(tag_links(d['text'], 'linkedin', 'social', date))
    payload = {'platform': 'linkedin', 'text': text, 'alt_text': d.get('alt_text') or d.get('topic') or ''}
    if d.get('image_url'):
        payload['image_url'] = d['image_url']
    ok, lines = call_make(payload)
    first = lines[0] if lines else ''
    if ok and first.startswith('POSTED linkedin '):
        urn = first.split(' ', 2)[2].strip()
        d['status'] = 'posted'; d['posted_at'] = now_iso(); d['posted_via'] = 'make'
        d['posted_url'] = f'https://www.linkedin.com/feed/update/{urn}/' if urn.startswith('urn:li:') else urn
        d.pop('error', None)
        return f'LinkedIn posted: {d["posted_url"]}'
    if first == 'Accepted':
        d['status'] = 'failed'; d['error'] = 'Make accepted the request but did not post (scenario route not matched).'
    else:
        d['status'] = 'failed'; d['error'] = ' '.join(lines)[:500] or 'No reply from Make'
    return f'LinkedIn failed: {d["error"]}'


def post_gbp(d, date):
    results = d.get('results') or {}
    if any((results.get(loc) or {}).get('status') == 'posted' for loc in LOCATIONS):
        # The scenario posts to both locations together, so a partly posted file is never sent again automatically.
        return 'Google Business: already partly posted; not sent again (finish the remaining location by hand).'
    if d.get('blog_url') and not blog_live(d['blog_url']):
        d['status'] = 'held'; d['held_reason'] = f'Blog not live when checked at {now_iso()}: {d["blog_url"]}'
        return 'Google Business held: blog not live'
    payload = {'platform': 'gbp', 'title': (d.get('topic') or '')[:58], 'summary': d['summary'],
               'cta_url': tag(d.get('cta_url') or d.get('blog_url') or 'https://equalpsychology.com.au', 'google', 'business-profile', date),
               'image_url': d.get('image_url') or ''}
    ok, lines = call_make(payload)
    for loc in LOCATIONS:
        hit = next((l for l in lines if l.startswith(f'POSTED gbp {loc} ')), None)
        if hit:
            results[loc] = {'status': 'posted', 'posted_at': now_iso(), 'id_or_url': hit.split(' ', 3)[3].strip(), 'via': 'make'}
    failed = next((l for l in lines if l.startswith('FAILED')), None)
    kew = re.match(r'FAILED gbp Croydon \(Kew posted: ([^)]+)\)', failed or '')
    if kew and kew.group(1).strip():
        results['Kew'] = {'status': 'posted', 'posted_at': now_iso(), 'id_or_url': kew.group(1).strip(), 'via': 'make'}
    for loc in LOCATIONS:
        if (results.get(loc) or {}).get('status') != 'posted':
            # A failure on Kew stops the scenario before Croydon; the reply names the location that failed.
            results[loc] = {'status': 'failed', 'error': (failed or ' '.join(lines) or 'No reply from Make')[:500]}
    posted = [loc for loc in LOCATIONS if results[loc]['status'] == 'posted']
    d['results'] = results
    d['status'] = 'posted' if len(posted) == len(LOCATIONS) else 'partial' if posted else 'failed'
    if posted:
        d['posted_at'] = now_iso(); d['posted_via'] = 'make'
    return f'Google Business {d["status"]}: ' + ', '.join(f'{k} {v["status"]}' for k, v in results.items())


def run(date, platforms, scheduled):
    # A queued run checks out the commit it was started on; read the latest queue first.
    try:
        git('pull', '--rebase', '-q')
    except subprocess.CalledProcessError as e:
        print(f'Could not update the checkout first: {e.stderr.strip()[:200]}')
    route = json.load(open(os.path.join(ROOT, 'posting.json')))
    changed, report = [], []
    for p in platforms:
        if scheduled and route.get(p) != 'make':
            report.append(f'{p}: routed to {route.get(p)}, left to that route.'); continue
        path = os.path.join(ROOT, QUEUE[p], f'{date}.json')
        if not os.path.exists(path):
            report.append(f'{p}: nothing scheduled for {date}.'); continue
        d = json.load(open(path, encoding='utf-8'))
        if scheduled and (d.get('slot') or 'morning') != 'morning':
            report.append(f'{p}: file is for the {d.get("slot")} slot.'); continue
        if d.get('status') != 'approved':
            report.append(f'{p}: status {d.get("status")}, not posted.'); continue
        report.append(post_linkedin(d, date) if p == 'linkedin' else post_gbp(d, date))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2); f.write('\n')
        changed.append(path)
    if changed:
        git('add', *changed)
        git('commit', '-m', f'Record Make posts for {date}')
        push()
    print('\n'.join(report) or 'nothing to do')
    return 1 if any(' failed' in r for r in report) else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date'); ap.add_argument('--platform', choices=['linkedin', 'gbp', 'all', 'check'], default='all')
    a = ap.parse_args()
    if not HOOK:
        print('MAKE_POST_WEBHOOK is not set yet; nothing to do.'); return 0
    if a.platform == 'check':
        # Reaches the scenario with a platform no route takes, so nothing is posted. Make replies "Accepted".
        ok, lines = call_make({'platform': 'check', 'text': 'connection check, posts nothing'})
        print('Make webhook check:', ' '.join(lines)[:200]); return 0 if lines[:1] == ['Accepted'] else 1
    platforms = ['linkedin', 'gbp'] if a.platform == 'all' else [a.platform]
    if a.date:
        return run(a.date, platforms, scheduled=False)
    now = datetime.now(MEL)
    if not 8 <= now.hour < 12:
        print(f'Not a posting window ({now:%H:%M} Melbourne).'); return 0
    return run(now.strftime('%Y-%m-%d'), platforms, scheduled=True)


if __name__ == '__main__':
    sys.exit(main())
