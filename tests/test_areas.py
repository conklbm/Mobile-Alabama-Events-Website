from pipeline import areas


def test_cities_map_to_areas_and_rings():
    assert (areas.area_of("Mobile"), areas.ring_of("mobile")) == ("mobile", "core")
    assert areas.area_of("dauphin island") == "mobile"
    assert (areas.area_of("Loxley"), areas.ring_of("eastern-shore")) == ("eastern-shore", "core")
    assert (areas.area_of("Orange Beach"), areas.ring_of("baldwin-coast")) == ("baldwin-coast", "outer")
    assert areas.area_of("Pensacola") == "pensacola" and areas.label("pensacola") == "Pensacola"
    assert areas.area_of("Atlanta") is None and areas.area_of("") is None


def test_draws():
    assert areas.is_draw("53rd Annual National Shrimp Festival", ["themobmom"])
    assert areas.is_draw("Daniel Tosh: My First Farewell Tour", ["ticketmaster"])
    assert not areas.is_draw("Indoor Cycling", ["orangebeach-city"])
    assert not areas.is_draw("Pensacola Bay Center Public Ice Skating 4:30-5:30pm", ["ticketmaster"])


def test_shows_on_site_by_ring():
    show = areas.shows_on_site
    assert show("mobile", ["coastal"], "Loxley", "Food Truck Friday", ["themobmom"])           # core: always
    assert not show("mobile", ["coastal"], "Orange Beach", "Yoga", ["orangebeach-city"])      # outer, not a draw
    assert show("mobile", ["coastal"], "Gulf Shores", "Shrimp Festival", ["themobmom"])       # outer draw
    assert show("mobile", ["mobile"], "", "Unknown place", ["92zew"])                         # no area: region tags decide
    assert not show("mobile", ["coastal"], "Somewhere", "Thing", ["x"])
    assert show("coastal", ["coastal"], "Orange Beach", "Yoga", ["x"])                       # other feeds ignore the rings


def test_pensacola_only_its_biggest_nights():
    show = lambda title, src, venue: areas.shows_on_site("mobile", ["coastal"], "Pensacola", title, src, venue)  # noqa: E731
    assert show("Jim Gaffigan: Everything is Wonderful!", ["ticketmaster"], "pensacola-bay-center")
    assert show("Daniel Tosh: My First Farewell Tour", ["ticketmaster"], "pensacola-saenger")
    assert not show("Saosin", ["ticketmaster"], "vinyl-music-hall")                                  # club show
    assert not show("Pensacola Ice Flyers vs. Macon Mayhem", ["ticketmaster"], "pensacola-bay-center")
    assert not show("The Billy Joel Legacy: Celebrating The Piano Man", ["ticketmaster"], "pensacola-saenger")
    assert not show("Kenny G-Green Room Lounge", ["ticketmaster"], "pensacola-saenger")
    assert show("Pensacola Seafood Festival", ["visit-pensacola"], None)                              # festivals still count
    # the Baldwin coast keeps the looser rule
    assert areas.shows_on_site("mobile", ["coastal"], "Orange Beach", "Some Band", ["ticketmaster"], "the-wharf-amphitheater")


def test_settings_regexes_survive_yaml():
    # YAML double quotes turn \b into a backspace; the patterns must arrive intact
    from pipeline import config
    o = config.settings()["outer_ring"]
    for pattern in [o["draw_words"], o["never"], *[a.get("never", "") for a in o.get("areas", {}).values()]]:
        assert not any(ord(c) < 32 for c in pattern), pattern
