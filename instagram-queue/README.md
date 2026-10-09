# Instagram posting queue

Each file `YYYY-MM-DD.json` is one approved Instagram post for @equal_psychology.
The scheduled posting task runs daily, publishes the file whose date matches the day in Melbourne,
and updates `status` from `approved` to `posted` (or `failed`, or `held`).

- `format` "reel": `video` is one public MP4 URL, published as a Reel.
- `media`: 1 image (single) or 2-10 images (carousel), public raw GitHub URLs, posted in order.
- `caption`: published exactly as written.
- `blog_url`: if set, the post is only published once that page is live. If it is not live, status becomes `held`.

Only files with `"status": "approved"` are ever published.

`pending_review` files are drafts awaiting Matthew or Natalia's approval and are never published.
