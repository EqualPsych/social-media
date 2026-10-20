#!/usr/bin/env python3
"""Post today's Instagram queue file to Instagram and the Facebook Page, straight through Meta's own API (free).

Runs from .github/workflows/meta-post.yml. Replaces the Zapier route for Instagram and Facebook once posting.json says
"meta" for them; until then it does nothing, so the two routes never both post.

Secrets (GitHub repository secrets, never printed): META_PAGE_TOKEN, a non-expiring Facebook Page access token for the
Equal Psychology Page with pages_manage_posts, pages_read_engagement, pages_show_list, instagram_basic,
instagram_content_publish (and instagram_manage_insights, read_insights for reports).

Rules mirror the Claude posting task: only "approved" files for today's Melbourne date and this run's slot; blog check
before posting anything blog-linked; Facebook gets the caption with the blog link and facebook_link_line, link tags on
equalpsychology.com.au links; companion Reels (share_to_feed false) stay off the grid and off Facebook; results are
written back into the queue file in the same fields as before.

    python3 scripts/meta_post.py                 # normal run (slot from the Melbourne clock)
    python3 scripts/meta_post.py --date 2026-10-26 --slot morning
    python3 scripts/meta_post.py --check         # check the token and account access, post nothing
"""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = 'https://graph.facebook.com/v21.0'
IG_USER = '17841467019342725'
PAGE = '117619581441312'
RAW = 'https://raw.githubusercontent.com/EqualPsych/social-media/'
MEL = ZoneInfo('Australia/Melbourne')
TOKEN = os.environ.get('META_PAGE_TOKEN', '').strip()


class MetaError(Exception):
    pass


def api(method, path, params=None):
    """One Graph API call. The token is sent in the body or query and never printed."""
    params = dict(params or {})
    params['access_token'] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f'{GRAPH}/{path}'
    req = urllib.request.Request(url + ('?' + data.decode() if method == 'GET' else ''), data=None if method == 'GET' else data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get('error', {})
            msg = f"{err.get('type', 'Error')} {err.get('code', '')}: {err.get('message', '')}".strip()
        except Exception:
            msg = f'HTTP {e.code}'
        raise MetaError(msg.replace(TOKEN, '***') if TOKEN else msg)


def git(*a):
    return subprocess.run(['git', '-C', ROOT, *a], check=True, capture_output=True, text=True).stdout.strip()


def tag(url, src, date):
    """Link tag so website visits from the post are counted (same rule as the Claude posting task)."""
    if not url.startswith('https://equalpsychology.com.au'):
        return url
    frag = ''
    if '#' in url:
        url, frag = url.split('#', 1)
        frag = '#' + frag
    sep = '&' if '?' in url else '?'
    return f'{url}{sep}utm_source={src}&utm_medium=social&utm_campaign=post-{date}{frag}'


def blog_live(url):
    try:
        req = urllib.request.Request(url, headers={'user-agent': 'Mozilla/5.0 (EqualPsych social poster)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(200000).decode('utf-8', 'ignore').lower()
            return r.status == 200 and 'page not found' not in body[:20000]
    except Exception:
        return False


def jpeg_urls(urls):
    """Instagram accepts JPEG only. Make a .jpg beside each PNG (once), commit it, and return commit-pinned URLs."""
    from PIL import Image
    out, made = [], False
    for u in urls:
        if not u.startswith(RAW + 'main/'):
            out.append(u); continue
        rel = u[len(RAW + 'main/'):]
        if rel.lower().endswith(('.jpg', '.jpeg')):
            out.append(rel); continue
        jrel = re.sub(r'\.png$', '.jpg', rel, flags=re.I)
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, jrel)
        if not os.path.exists(dst):
            Image.open(src).convert('RGB').save(dst, 'JPEG', quality=92, optimize=True)
            made = True
        out.append(jrel)
    if made:
        git('add', *[p for p in out if not p.startswith('http')])
        git('commit', '-m', 'JPEG copies for Instagram')
        push()
    sha = git('rev-parse', 'HEAD')
    return [p if p.startswith('http') else f'{RAW}{sha}/{p}' for p in out]


def push():
    for _ in range(3):
        try:
            git('pull', '--rebase', '-q')
            git('push', '-q')
            return
        except subprocess.CalledProcessError:
            time.sleep(5)
    raise RuntimeError('could not push')


def wait_ready(container, tries=20, gap=15):
    for _ in range(tries):
        s = api('GET', container, {'fields': 'status_code,status'})
        code = s.get('status_code')
        if code == 'FINISHED':
            return
        if code in ('ERROR', 'EXPIRED'):
            raise MetaError(f"media processing {code}: {s.get('status', '')}")
        time.sleep(gap)
    raise MetaError('media still processing after waiting')


def post_instagram(d):
    fmt, cap = d.get('format'), d.get('caption', '')
    if fmt == 'reel':
        params = {'media_type': 'REELS', 'video_url': d['video'], 'caption': cap}
        if d.get('share_to_feed') is False:
            params['share_to_feed'] = 'false'
        c = api('POST', f'{IG_USER}/media', params)['id']
        wait_ready(c)
    else:
        media = jpeg_urls(d['media'])
        if len(media) == 1:
            c = api('POST', f'{IG_USER}/media', {'image_url': media[0], 'caption': cap})['id']
            wait_ready(c, tries=8, gap=5)
        else:
            kids = []
            for m in media[:20]:
                k = api('POST', f'{IG_USER}/media', {'image_url': m, 'is_carousel_item': 'true'})['id']
                kids.append(k)
            for k in kids:
                wait_ready(k, tries=8, gap=5)
            c = api('POST', f'{IG_USER}/media', {'media_type': 'CAROUSEL', 'children': ','.join(kids), 'caption': cap})['id']
            wait_ready(c, tries=8, gap=5)
    pid = api('POST', f'{IG_USER}/media_publish', {'creation_id': c})['id']
    try:
        link = api('GET', pid, {'fields': 'permalink'}).get('permalink')
    except MetaError:
        link = None
    return pid, link


def facebook_message(d, date):
    lines = d.get('caption', '').split('\n')
    if d.get('blog_url'):
        for i, l in enumerate(lines):
            if 'link in bio' in l.lower():
                lines[i] = 'Read the full article: ' + tag(d['blog_url'], 'facebook', date)
                break
    msg = '\n'.join(lines)
    extra = d.get('facebook_link_line')
    if extra:
        extra = re.sub(r'https://equalpsychology\.com\.au[^\s)]*', lambda m: tag(m.group(0), 'facebook', date), extra)
        ls = msg.split('\n')
        idx = max((i for i, l in enumerate(ls) if l.startswith('#')), default=None)
        if idx is None:
            msg = msg.rstrip() + '\n\n' + extra
        else:
            msg = '\n'.join(ls[:idx]).rstrip() + '\n\n' + extra + '\n\n' + '\n'.join(ls[idx:])
    return msg


def post_facebook(d, date):
    msg = facebook_message(d, date)
    if d.get('format') == 'reel':
        r = api('POST', f'{PAGE}/videos', {'file_url': d['video'], 'description': msg})
        return r.get('id')
    media = d.get('media') or []
    if len(media) == 1:
        r = api('POST', f'{PAGE}/photos', {'url': media[0], 'message': msg})
        return r.get('post_id') or r.get('id')
    ids = [api('POST', f'{PAGE}/photos', {'url': m, 'published': 'false'})['id'] for m in media[:10]]
    params = {'message': msg}
    for i, pid in enumerate(ids):
        params[f'attached_media[{i}]'] = json.dumps({'media_fbid': pid})
    return api('POST', f'{PAGE}/feed', params).get('id')


def now_iso():
    return datetime.now(MEL).isoformat(timespec='seconds')


def run(date, slot):
    flags = json.load(open(os.path.join(ROOT, 'posting.json')))
    ig_on, fb_on = flags.get('instagram') == 'meta', flags.get('facebook') == 'meta'
    if not (ig_on or fb_on):
        print('posting.json does not route Instagram or Facebook to Meta yet; nothing to do.')
        return 0
    path = os.path.join(ROOT, 'instagram-queue', f'{date}.json')
    if not os.path.exists(path):
        print(f'{date}: no Instagram file.'); return 0
    d = json.load(open(path, encoding='utf-8'))
    if (d.get('slot') or 'morning') != slot:
        print(f'{date}: file is for the {d.get("slot") or "morning"} slot.'); return 0
    report, changed = [], False
    if d.get('status') != 'approved' and not (fb_on and d.get('status') == 'posted' and not (d.get('facebook') or {}).get('status') == 'posted'):
        print(f'{date}: status {d.get("status")}, not posted.'); return 0
    if d.get('blog_url') and d.get('status') == 'approved' and not blog_live(d['blog_url']):
        d['status'] = 'held'; d['held_reason'] = f'Blog not live when checked at {now_iso()}: {d["blog_url"]}'
        changed = True; report.append('held: blog not live')
    else:
        if ig_on and d.get('status') == 'approved':
            try:
                pid, link = post_instagram(d)
                d['status'] = 'posted'; d['posted_at'] = now_iso(); d['posted_url'] = link or pid; d['posted_via'] = 'meta'
                report.append(f'Instagram posted: {link or pid}')
            except Exception as e:
                d['status'] = 'failed'; d['error'] = str(e)[:500]; report.append(f'Instagram failed: {e}')
            changed = True
        if fb_on and d.get('facebook_mirror') is not False and (d.get('facebook') or {}).get('status') != 'posted':
            try:
                fid = post_facebook(d, date)
                d['facebook'] = {'status': 'posted', 'posted_at': now_iso(), 'id_or_url': fid, 'via': 'meta'}
                report.append(f'Facebook posted: {fid}')
            except Exception as e:
                d['facebook'] = {'status': 'failed', 'error': str(e)[:500]}; report.append(f'Facebook failed: {e}')
            changed = True
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2); f.write('\n')
        git('add', path)
        git('commit', '-m', f'Record Meta posts for {date} ({slot})')
        push()
    print('\n'.join(report) or 'nothing changed')
    return 1 if any('failed' in r for r in report) else 0


def check():
    ig = api('GET', IG_USER, {'fields': 'username,followers_count'})
    page = api('GET', PAGE, {'fields': 'name,followers_count'})
    lim = api('GET', f'{IG_USER}/content_publishing_limit', {'fields': 'quota_usage,config'})
    perms = api('GET', 'me', {'fields': 'id,name'})
    print(f"Token works. Instagram @{ig.get('username')} ({ig.get('followers_count')} followers); Page {page.get('name')}; "
          f"publishing used {lim.get('data', [{}])[0].get('quota_usage')} of {lim.get('data', [{}])[0].get('config', {}).get('quota_total')} in 24 hours; token belongs to {perms.get('name')}.")
    # Can this token read Instagram reach, saves and shares? (Needs an insights permission; Meta has renamed these over
    # time, so test the call itself rather than look for a permission name.)
    try:
        last = api('GET', f'{IG_USER}/media', {'fields': 'id', 'limit': '1'}).get('data', [{}])[0].get('id')
        ins = api('GET', f'{last}/insights', {'metric': 'reach,saved,shares'}) if last else {}
        print('Instagram insights: available (' + ', '.join(f"{m['name']} {m['values'][0]['value']}" for m in ins.get('data', [])) + ' on the latest post)')
    except MetaError as e:
        print('Instagram insights: not available with this token (' + str(e)[:160] + ')')
    try:
        dbg = api('GET', 'debug_token', {'input_token': TOKEN}).get('data', {})
        exp = dbg.get('expires_at')
        print('Token expiry:', 'never' if not exp else datetime.fromtimestamp(exp, MEL).isoformat(), '| scopes:', ', '.join(dbg.get('scopes', [])))
    except MetaError as e:
        print('(Could not read token details:', e, ')')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date'); ap.add_argument('--slot', choices=['morning', 'evening']); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not TOKEN:
        print('META_PAGE_TOKEN is not set yet; nothing to do.'); return 0
    if a.check:
        return check()
    now = datetime.now(MEL)
    # The workflow fires twice for each slot (one hour apart, so daylight saving is covered); the window takes the first
    # run at or after 8:22am and 7:52pm, and the second finds the post already recorded.
    slot = a.slot or ('morning' if 8 <= now.hour < 10 else 'evening' if 19 <= now.hour < 21 else None)
    if not slot:
        print(f'Not a posting window ({now:%H:%M} Melbourne).'); return 0
    return run(a.date or now.strftime('%Y-%m-%d'), slot)


if __name__ == '__main__':
    sys.exit(main())
