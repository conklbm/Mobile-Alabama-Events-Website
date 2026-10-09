# Review routine notes — 2026-10-09 (issue #9)

## Resolved automatically

- **Schreiber Water Treatment Plant** (new venue, slug `schreiber-water-treatment-plant`) — 120-B County Road 20, Foley, AL 36535. Riviera Utilities' new water plant, named for former board member Bob Schreiber; replaces the utility's old South Water Plant. Source: [Riviera Utilities' own announcement](https://www.rivierautilities.com/newsroom/riviera-to-host-dedication-commissioning-ceremony-for-the-schreiber-water-treatment-facility), which gives the same address as the issue (`#941`).
- **Bill-E's** (new venue, slug `bill-es-fairhope`) — 19992 State Highway 181, Fairhope, AL 36532. Bacon-themed restaurant/smokehouse that runs its own community events. Added in case a future "BILL-E's BACON, BURGERS, & BIKES" listing comes through with the venue name actually populated (see "Needs Brooks" — this run's two occurrences didn't). Sources: [USDA FSIS establishment listing](https://www.fsis.usda.gov/inspection/fsis-inspected-establishments/bill-es-small-batch-bacon-llc) (19992 Hwy 181) and the [Eastern Shore Chamber business directory listing](https://business.eschamber.com/list/member/bill-e-s-8758) (same address, hours, phone).
- **Lowes Kid Workshops – Firefighting Plane** (`#682`) — added to `force_publish` in `overrides.yaml`, same pattern as the existing Fall Brawl Festival entry. This is Lowe's national Kids Workshop program, which runs the same Saturday at participating stores nationwide; nothing ties it to one specific Mobile-area store (confirmed via web search — no single-store match found, every source describes it as a multi-store program), so a single address would be a guess. Publishing as-is beats guessing a store.

## Needs Brooks

**`#192` Adult Talent Show, Crescent Theater, Sat Oct 24** — flagged as possibly cancelled (TicketWeb stopped listing it two runs running). I could not reach the specific TicketWeb page directly (DNS blocked in this environment), and a web search found several *other* current Crescent Theater TicketWeb listings (comedy shows dated into November) but no Adult Talent Show — suggestive but not conclusive that it's off sale. Recommend checking the venue's listing directly, then:
`cancel 192` (if it's gone) or `not-cancelled 192` (if it's still on sale).

**`#932` / `#965` The Moonlight Chasse' Ballroom Dance Society (Nov 2, Dec 7)** — this recurring series already has a resolved venue elsewhere on the site (Oct 19's occurrence links to `/venues/hot-wheels-skating-rink/`, 616 Whispering Pines Rd, Daphne — already in `venues.yaml`). I confirmed via web search that this dance society has used Hot Wheels Skating Rink/Center for years. But the Eastern Shore Chamber collector returned a **blank** venue name *and* blank address for these two specific occurrences (not a vocabulary gap — there's no raw text for an alias to match against), so no edit to `venues.yaml` can resolve them automatically; I verified this against the actual resolver code before writing anything. Two options:
`approve 932 965` (publish as-is, venue will show blank on the page), or leave held until the Chamber's page starts returning a location for these dates again.

**`#937` / `#964` BILL-E's BACON, BURGERS, & BIKES (Nov 6, Dec 6)** — same blank-venue-and-address situation as above. I added Bill-E's to `venues.yaml` (see above) in case it helps on a future run where the source actually returns a venue string, but these two occurrences specifically can't be auto-resolved for the same reason. `approve 937 964` if you want them live now.

If blank venue+address keeps showing up from `eastern-shore-chamber`, it's probably worth a look at the collector itself (some listing pages on that GrowthZone "classic" layout may be omitting location in a format the parser doesn't catch) — but that's outside what this routine edits.

## Validation
`uv sync`, `uv run pytest -q` (62 passed), YAML loads clean, `pipeline process` + `pipeline queue` confirm: the two address/override fixes resolved, the 5 remaining items above are the only ones still open.
