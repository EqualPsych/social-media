#!/usr/bin/env python3
"""Check the posting schedule against the Zapier allowance.

Zapier's free plan gives 100 tasks a month and every successful Zapier call made by Claude uses 2 tasks, so there are
50 calls a month. The allowance renews on the 23rd. The posting task runs at 8:22am Melbourne, which is still the
previous day in UTC, so a post dated the 23rd (Melbourne) is counted in the cycle that is ending. Cycles here therefore
run from the 24th to the 23rd of the next month, by queue date.

Calls per item: Instagram post 1; its Facebook copy 1 (unless "facebook_mirror": false); an off-grid companion Reel
at most 7 (create, up to 4 processing checks, publish, grid check); LinkedIn post 1; Google Business post 1 per location.
Reports: the monthly report on the 1st is limited to 6 calls. RESERVE calls are kept spare in every cycle.
Only files with status "approved" are counted.

    python3 scripts/zapier_budget.py          # prints each cycle and fails if one is over
"""
import glob, json, os, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALLS_PER_CYCLE, REPORT, RESERVE = 50, 6, 4

def cycle(ds):
    d = date.fromisoformat(ds)
    y, m = (d.year, d.month) if d.day >= 24 else ((d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12))
    return f'{y}-{m:02d}-24'

def main():
    route = json.load(open(os.path.join(ROOT, 'posting.json')))
    C = {}
    for q in ('instagram-queue', 'linkedin-queue', 'gbp-queue'):
        for f in glob.glob(os.path.join(ROOT, q, '2*.json')):
            d = json.load(open(f, encoding='utf-8'))
            if d.get('status') != 'approved': continue
            if q == 'instagram-queue':
                n = 0 if route.get('instagram') == 'meta' else (7 if d.get("share_to_feed") is False else 1)
                n += 0 if d.get('facebook_mirror') is False or route.get('facebook') == 'meta' else 1
            elif q == 'linkedin-queue': n = 0 if route.get('linkedin') in ('meta', 'make') else 1
            else: n = 0 if route.get('gbp') in ('meta', 'make') else len(d.get('locations') or {})
            c = C.setdefault(cycle(d['date']), {'posts': 0, 'calls': 0})
            c['posts'] += 1; c['calls'] += n
    bad = False
    for k in sorted(C):
        total = C[k]['calls'] + REPORT
        ok = total + RESERVE <= CALLS_PER_CYCLE
        bad |= not ok
        print(f"cycle from {k}: {C[k]['posts']} posts, {C[k]['calls']} calls + {REPORT} report = {total} of {CALLS_PER_CYCLE} ({'ok' if ok else 'OVER, keep ' + str(RESERVE) + ' spare'})")
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
