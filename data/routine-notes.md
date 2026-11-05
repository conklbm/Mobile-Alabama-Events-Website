# Routine notes — issue #21 (2026-11-05)

## Resolved automatically

**New venues added to `data/venues.yaml`:**

- **Shiloh Baptist Church** — 717 Cleveland Rd, Saraland, AL 36571. Source: [Superpages](https://www.superpages.com/saraland-al/bpp/shiloh-baptist-church-8448505), corroborated by ChurchesList and Christianity.com directories.
- **Swift-Coles Historic Home** — 17424 Swift Coles Ln, Bon Secour, AL 36511 (not Bay Minette — corrected). Marked `coastal` (Bon Secour sits between Foley and Gulf Shores). Source: Alabama historical marker database, Alabama tourism site, Digital Alabama (3 independent agreeing sources).
- **Tameron Buick GMC** — 27161 US Highway 98, Daphne, AL 36526. Source: [tameronbuickgmc.com](https://www.tameronbuickgmc.com/service/index.htm), Kelley Blue Book dealer listing.
- **PetSmart (Foley)** — 2498 S McKenzie St, Foley, AL 36535. Marked `coastal`. Source: [petsmart.com store page](https://www.petsmart.com/stores/us/al/foley-store2722.html).
- **The Blowout Bar** — 6601 Airport Blvd, Suite B, Mobile, AL 36608. Source: [Bay Business News](https://baybusinessnews.com/dermatology-cosmetology/the-blowout-bar-opens-in-mobile/).
- **Great Day Latte** — 10 S Conception St, Mobile, AL 36602 (zip inferred from the downtown block; not stated explicitly by any source — flag if it ever needs correcting). Source: [Fox10 ribbon-cutting coverage](https://www.fox10tv.com/2024/10/18/great-day-latte-holds-ribbon-cutting-ceremony/), Downtown Mobile Alliance listing.
- **Muffinjaw Designs** — 610 St Anthony St, Mobile, AL 36602. Source: downtownmobile.org listing.
- **Grace on Dauphin** — 555 Dauphin St, Mobile, AL 36602 (the restaurant trades as "Grace" on OpenTable; the event title's "Grace on Dauphin" matches the address exactly). Source: [OpenTable](https://www.opentable.com/r/grace-mobile), Mobile Bay Magazine.
- **Joseph C. Dotch Community Center & Park** — 3100 Bank Ave, Mobile, AL 36617. Source: cityofmobile.gov.
- **River Delta Marina & Campground** — 2350 Dead Lake Marina Rd, Creola, AL 36525. Source: Alabama tourism, Mobile County park listing.
- **Press & Co.** — 711 Belrose Ave, Daphne, AL 36526 (cafe/juicery named in the event title). Source: [Bay Business News](https://baybusinessnews.com/hospitality/press-co-announces-grand-opening/), Gulf Coast News Today.
- **Page & Palette** — 32 S Section St, Fairhope, AL 36532. Source: [pageandpalette.com](https://www.pageandpalette.com/), The Bama Buzz.
- **Dave & Buster's (Mobile)** — 1757 E Interstate 65 Service Rd, Mobile, AL 36606 (opened Jan 2025 — Mobile's first location). Source: [OpenTable](https://opentable.ca/r/dave-and-busters-mobile), Nation's Restaurant News.

**Aliases added to existing venues:**

- "217 S. Sage Avenue" → `st-pius-x-catholic-church` (St. Pius X hosts the Merry Midtown Market at its own address; [Fox10](https://www.fox10tv.com/2024/11/08/merry-midtown-market)).
- "The Conde-Charlotte Museum" → `conde-charlotte-museum-house`.
- "30500 State Hwy 181, Suite 134 Spanish Fort, AL, 36527" → `the-bull-spanish-fort` (same restaurant, chamber's address format differs slightly from the alias already on file).
- "The Admiral", "Le Moyne's Chophouse" (both apostrophe styles) → `the-admiral-hotel`. Le Moyne's Chophouse is the hotel's onsite restaurant, confirmed via [Michelin Guide](https://guide.michelin.com/en/hotels-stays/mobile/the-admiral-hotel-14596) and downtownmobile.org — not a separate venue.
- "68 Ventures Bowl" → `hancock-whitney-stadium` (the bowl game's name, not a separate stadium; confirmed via usajaguars.com and the bowl's own site).
- "Waffles R Wild – OWA" / "Waffles R Wild" → `owa-parks-resort` (restaurant inside the OWA complex, same pattern as the other OWA sub-venues already aliased there).

**Overrides applied (`data/overrides.yaml`):**

- `not_cancelled`: #795 Historical Lecture Series: The Pelican Girls (Nov 15) — still listed on historicmobile.org and mobilecountyal.gov, same date/venue.
- `never_merge`: [1559, 1558] USA Wind Ensemble Fall Concert vs. USA Symphony Band Fall Concert — confirmed these are two different university ensembles that each hold their own fall concert at Laidlaw, historically on separate nights.
- `force_publish` (blank `venue_name_raw` at the source — alias can't match, but the real venue is now confirmed and on file):
  - #1508 Bayside Boys Book Signing — Page & Palette, Fairhope.
  - #1413 Spirit Night Fundraiser at Dave & Busters — Dave & Buster's, Mobile.
  - #1451 43rd Mobile International Festival — The Grounds, Mobile (confirmed via mobilecountyal.gov and alabama.travel).
  - #1534 The Moonlight Chasse' Ballroom Dance Society (Jan 5) — Hot Wheels Skating Rink, Daphne (same recurring series already force-published twice before for the same blank-raw issue).

Ran `pytest` (69 passed), validated both YAML files, and re-ran `pipeline process`/`queue`/`publish` locally — all of the above cleared the queue as expected with no errors.

## Needs Brooks

Could not confirm, or genuinely ambiguous — left out of `venues.yaml`/`overrides.yaml` rather than guessed:

- **#1512 "The Taste of The Ruff"** — raw venue is "1317 Johnson Road; Daphne, Alabama 36526." No business indexed at that exact address (neighboring parcels are vacant/residential); the eastern-shore-chamber event page didn't resolve from this session's network. `venue new-slug "Name" Daphne` once you know what's there, or `ignore 1512`.
- **#1441 "Midtown Vintage Market"** — raw venue is "156 S. Florida Street," Mobile. No business matches that exact address among nearby Florida St commercial listings. `venue new-slug "Name" Mobile` or `ignore 1441`.
- **#1222 "Taste of Christmas Festival"** — raw venue is just "Piggly Wiggly." Several Piggly Wiggly stores host similar fall/holiday events in the Mobile area (University Blvd, Saraland); couldn't confirm which one this specific listing means. `venue new-slug "Piggly Wiggly (___)" ___` with the right store, or `ignore 1222`.
- **#1509 "Eastern Shore Children's Clinic - Open House celebrating 50 years"** — blank raw venue. The clinic has two offices (150 S Ingleside St Suite 7, Fairhope; and a newer Spanish Fort office, address not found) and I can't tell which one is throwing the 50th-anniversary open house. `venue eastern-shore-childrens-clinic-fairhope "Eastern Shore Children's Clinic" Fairhope` if it's the Fairhope office, or `ignore 1509`.
- **#1527 "Christmas Tour of Homes"** (eastern-shore-chamber) — blank raw venue. Tour-of-homes events typically span several private homes with no single venue; couldn't confirm a fixed starting location for this one. Probably just `ignore 1527`.
- **#1148 "Young Professionals of Mobile December 2026 Social"** — blank raw venue. Source is my.mobilechamber.com, the same host that's 403-Forbidden-blocked in this week's source alerts, so nothing could be checked there or found elsewhere. `ignore 1148` until the Mobile Chamber source access is sorted out.
- **#632 "Hollywood in Your Pocket - The Art of Iphone Photography"** (possibly cancelled, Eastern Shore Art Center, Nov 6) — no trace of this specific class anywhere online; couldn't confirm it's still on or that it's been pulled. `not-cancelled 632` or `cancel 632`.
- **#1060 "Corks, Casks, and Canvas"** (possibly cancelled, ESAC, Nov 20) — this is ESAC's real annual fundraiser, but I only found a confirmed 2025 date (Oct 25); no 2026 date turned up to check against Nov 20. `not-cancelled 1060` or `cancel 1060`.
- **#646 / #1067 "Sculpting the Figure"** (possibly cancelled, ESAC, Jan 1 & Jan 8 2027) — no listing found either way. `not-cancelled 646 1067` or `cancel 646 1067`.
- **#657 "Painting with Pan Patels"** (possibly cancelled, ESAC via Downtown Fairhope, Jan 6 2027) — "Pan Patels" doesn't match any instructor or class I could find; the closest hit was "PanPastels" (an art material), so this may be a source-side data error rather than a real cancellation question. Worth a look at the raw listing. `not-cancelled 657` or `cancel 657`.
- **Source alerts** (not investigated — out of scope for this routine): 92ZEW returned 39 events vs. an expected 40 (likely just noise); Mobile Chamber's calendar pull is still 403 Forbidden.

**Side note:** re-running `pipeline process` to apply the above also pushed several occurrences over the two-consecutive-miss cancellation threshold that weren't in the original issue — six Tuesday Teen Art Club dates (Mobile Museum of Art), one Mobile County Parks Fall Festival (Nov 14), and one Crescent Comedy Workshop (Nov 18). These will show up in the "Still open" list this push generates; they weren't researched this round.
