# LinkedIn infographics

Template for the "Research for practice" graphic that goes with every LinkedIn post (1080×1350).

1. Copy this folder to `/home/claude/ig/li/` (with `/home/claude/ig` set up as in `tools/feed`: fonts installed, Drive logos saved as `logo_white_b64.txt` and `logo_yellow_b64.txt`).
2. Replace the `page(...)` calls at the bottom of `build.py` with the new posts. Name each file `<post date>-<slug>`, using the queue date of the post it belongs to.
3. `python3 build.py && node render.js` (prints overflow; `m` must be 0), then copy `png/<file>.png` to `linkedin/<YYYY-MM>/` and set the queue file's `image_url`.

Themes: `teal`, `cream`, `butter` (Pale Yellow), `white`. No Near Black backgrounds or bands.
Blocks: `pill`, `h1` (one `*call-out*`), `list` (dots or `'num'`), `chips`, `table` (two columns), `q` (label, question), `line`, `note`.
