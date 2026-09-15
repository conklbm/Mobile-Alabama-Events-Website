# Manual events (Facebook weekly scan)

~10 minutes a week. Scan: your Events tab, VisitMobile, Downtown Mobile Alliance,
Lagniappe, City of Mobile, Mobile Parks & Rec. Add one row per event to `events.csv`.

| column | required | format |
|---|---|---|
| title | yes | |
| start | yes | `2026-10-03 18:00` (local, America/Chicago) or `2026-10-03` for all-day |
| end | no | same format |
| venue | yes | must match a name or alias in `data/venues.yaml`, or it goes to review |
| city | no | overrides venue city |
| price | no | `Free`, `$10`, `$10-25` |
| info_url | yes | the page you saw it on |
| ticket_url | no | |
| category | no | music, family, food, arts, sports, community, nightlife |
| description | no | plain text |
| image_url | no | only if you have rights to reuse it |
| image_credit | no | |

Rows for past events can be deleted any time; they're already archived in `raw_pulls`.
