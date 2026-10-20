# Zapier budget

Set 21 Oct 2026. The practice's Zapier plan gives **100 tasks a month**, renewing on the **23rd**. Every successful
Zapier call made by Claude uses **2 tasks**, so there are **50 calls a month** for all posting and reporting.
(Source: Zapier, "How Zapier MCP usage works": each successful tool call uses two tasks; failed calls use none.)

The posting task runs at 8:22am Melbourne, which is still the previous day in UTC, so a post dated the 23rd is counted
in the cycle that is ending. Cycles therefore run from the **24th to the 23rd**, by queue date.

## What each item costs

| Item | Calls |
|---|---|
| Instagram post | 1 |
| Its Facebook copy | 1 (none with `"facebook_mirror": false`) |
| Off-grid companion Reel | up to 7 (create, up to 4 processing checks, publish, grid check) |
| LinkedIn post | 1 |
| Google Business post | 1 per location (2) |
| Monthly report (1st) | up to 6 |
| Weekly interaction tracking | paused (it used about 25 calls a week) |

Keep at least 4 calls spare each cycle. Check with `python3 scripts/zapier_budget.py` after every schedule change; it
fails if a cycle is over. Claude must not make Zapier calls from a working session (tests, checks) unless asked: they
come out of the same 50.

## Plan

- **21 to 23 Oct:** no tasks left. Nothing posts. The posts that were due moved:
  Meaning carousel and Google post 21 Oct to 26 Oct; Meaning single 28 Oct to 31 Oct;
  ADHD overview carousel 23 Oct to 28 Oct; LinkedIn double empathy 22 Oct to 28 Oct.
- **24 Oct to 23 Nov (cycle 1):** every Instagram, LinkedIn and Google post goes out. Facebook copies only for the
  ADHD series posts (they carry the assessment link). The three companion Reels (5, 16, 19 Nov) are on hold.
- **24 Nov to 23 Dec (cycle 2):** Facebook copies back on for all posts; companion Reels on 30 Nov and 18 Dec.

## Options if more is wanted

A paid Zapier plan with more tasks would allow Facebook copies, companion Reels and the weekly tracking again.
