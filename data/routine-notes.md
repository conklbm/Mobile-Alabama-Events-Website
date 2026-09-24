# Routine notes — 2026-09-24

Reviewed issue #5 ("8 items need review — 2026-09-24", run #11). Only an "Unknown venues"
section was present (no possibly-cancelled, ambiguous matches, uncertain dates, or source
alerts this run).

## Resolved automatically

Added 7 new venues to `data/venues.yaml`:

- **DICK'S House of Sport (Mobile)** — 1390 Tingle Circle W, Ste B-3, Mobile, AL 36606.
  Source: [stores.dickssportinggoods.com](https://stores.dickssportinggoods.com/al/mobile/1647/)
- **Laun Park** — 5401 Windmill Dr, Mobile, AL 36693 (city park in Terrace Hills, splash pad
  opened July 2025). Source: [cityofmobile.gov](https://www.cityofmobile.gov/parks-rec/laun-community-center-park/)
- **Annunciation Greek Orthodox Church** — 50 S Ann St, Mobile, AL 36604 (raw listing had
  "An Street", a typo for "Ann Street"; confirmed via the event's own organizer site).
  Source: [greekfestmobile.com](https://greekfestmobile.com/contact/), [Yelp](https://www.yelp.com/biz/annunciation-greek-orthodox-church-mobile)
- **Lily Baptist Church** — 358 Kennedy St, Mobile, AL 36603.
  Source: [FaithStreet](https://www.faithstreet.com/church/lily-baptist-church-mobile-al)
- **Saraland Church** — 907 Shelton Beach Rd, Saraland, AL 36571 (Assemblies of God; runs
  CITYFEST). Source: [saralandchurch.com](https://www.saralandchurch.com/about), [Yelp](https://www.yelp.com/biz/saraland-church-saraland)
- **First Baptist Church of Satsuma** — 5600 Old Hwy 43, Satsuma, AL 36572.
  Source: [fbcsatsuma.com](https://mobilebaptists.org/business-directory/337/satsuma-first-baptist-church/), [Yelp](https://www.yelp.com/biz/first-baptist-church-of-satsuma-satsuma)
- **Celeste Road Baptist Church** — 10175 Celeste Rd, Saraland, AL 36571.
  Source: [celesteroadbaptist.com](https://celesteroadbaptist.com/)

## Needs Brooks

- **`2700 Newman Road – Mobile, Al`** — `#385` Fall Brawl Festival, Sat Oct 10. That address
  is a cluster of auto-salvage/junkyards (Newman Auto Recyclers, Heritage Used Car & Truck
  Parts) — nothing I can confirm hosts a family festival there, and I found no listing for a
  "Fall Brawl Festival" anywhere in Mobile. Could be a mis-typed address on the source listing.
  Recommend checking the themobmom listing directly (it was unreachable from this session —
  egress-blocked) or Brooks's own knowledge of the event before adding a venue.
  Ready-to-send once confirmed: `venue fall-brawl-venue-slug "Venue Name" Mobile`. Until then:
  `ignore 385` if it looks bogus, or leave held.

Two more items are now sitting in the local review queue (`#167` Corey O'Brien —
`cancellation_flagged`, Downtown Mobile; `#333` Coffee with the Chamber: Calagaz Printing —
`cancellation_flagged`, 90 Springdale Blvd) but neither was part of issue #5 — they surfaced
only when I re-ran `pipeline process` locally to validate this change. They'll show up in a
future review issue if still flagged next week; not acted on here.
