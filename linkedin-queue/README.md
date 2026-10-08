# LinkedIn posting queue

Each file `YYYY-MM-DD.json` is one approved LinkedIn post for the Equal Psychology company page.
A scheduled task runs on posting days, publishes the file whose date matches the day in Melbourne,
and updates `status` from `approved` to `posted` (or `failed`).

Only files with `"status": "approved"` are ever published. Text is published exactly as written.
