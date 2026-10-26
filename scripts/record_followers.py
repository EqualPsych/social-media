#!/usr/bin/env python3
"""Record this week's follower totals for Instagram and the Facebook Page (free, straight through Meta's API).

Runs every Monday from .github/workflows/followers-weekly.yml (27 Oct 2026; Matt asked to see followers gained or lost
week by week on each channel in the website's admin Social tab). Adds or updates one entry for today's Melbourne date in
reports/social/interactions.json "followers", which build_dashboard.py passes to the website. It uses no Zapier tasks.

LinkedIn and Google Business are not recorded here: there is no LinkedIn token outside Zapier, and Google no longer
gives a follower count. LinkedIn totals come from the monthly social report (Zapier call, or the analytics export).

    python3 scripts/record_followers.py           # record today's totals
    python3 scripts/record_followers.py --dry-run # fetch and print, write nothing
"""
import argparse, json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_post import api, MetaError, IG_USER, PAGE, TOKEN, ROOT  # noqa: E402

PATH = os.path.join(ROOT, 'reports/social/interactions.json')


def fetch():
    """Current totals. A platform that fails is left out (never written as 0)."""
    out, errors = {}, []
    for key, obj, fields in (('instagram', IG_USER, 'followers_count'), ('facebook', PAGE, 'followers_count')):
        try:
            n = api('GET', obj, {'fields': fields}).get('followers_count')
            if isinstance(n, int) and n >= 0:
                out[key] = n
            else:
                errors.append(f'{key}: no follower count returned')
        except MetaError as e:
            errors.append(f'{key}: {e}')
    return out, errors


def record(counts, today):
    data = json.load(open(PATH, encoding='utf-8'))
    rows = data.setdefault('followers', [])
    row = next((r for r in rows if r.get('date') == today), None)
    if row is None:
        row = {'date': today}
        rows.append(row)
    row.update(counts)
    rows.sort(key=lambda r: r.get('date', ''))
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if not TOKEN:
        print('META_PAGE_TOKEN is not set')
        return 1
    today = datetime.now(ZoneInfo('Australia/Melbourne')).date().isoformat()
    counts, errors = fetch()
    for e in errors:
        print('Could not read', e)
    if not counts:
        return 1
    if a.dry_run:
        print(today, counts)
        return 0
    print('Recorded', record(counts, today))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
