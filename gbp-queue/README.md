# Google Business Profile posting queue

Each file `YYYY-MM-DD.json` is one approved GBP post, published to every location listed (Kew and Croydon).
The scheduled posting task publishes the file whose date matches the day in Melbourne and records a result per location
in `results`, then sets `status` to `posted`, `partial`, `failed` or `held` (blog not live yet).
Only files with `"status": "approved"` are ever published. The summary is published exactly as written.
