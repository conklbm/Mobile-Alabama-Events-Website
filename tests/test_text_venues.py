from pipeline.scoring import is_self_promoted
from pipeline.text import clean_title, is_free_price, norm_key, slugify, strip_html, title_key
from pipeline.venues import VenueResolver

VENUES = [
    {"slug": "saenger-theatre", "name": "Saenger Theatre", "aliases": ["Mobile Saenger", "The Saenger"], "domains": ["mobilesaenger.com"], "city": "Mobile", "regions": ["mobile"]},
    {"slug": "moes-bbq", "name": "Moe's Original BBQ (Downtown Mobile)", "aliases": ["Moe's Original BBQ", "Moes BBQ"], "domains": [], "city": "Mobile", "regions": ["mobile"]},
    {"slug": "gs-city-hall", "name": "Gulf Shores City Hall", "aliases": ["1905 W 1st St"], "domains": ["gulfshoresal.gov"], "city": "Gulf Shores", "regions": ["coastal"]},
]
r = VenueResolver(VENUES, fuzzy_threshold=90)


def test_strip_html_and_entities():
    assert strip_html("<p>Moe&#8217;s <b>BBQ</b>&nbsp; live</p>") == "Moe’s BBQ live"
    assert clean_title("Beer, BBQ &#038; Bingo") == "Beer, BBQ & Bingo"


def test_keys():
    assert norm_key("Moe’s Original BBQ!") == "moe s original bbq"
    assert title_key("The Beer, BBQ & Bingo Show (2026)") == "beer bbq bingo"
    assert slugify("Beer, BBQ & Bingo — Moe's") == "beer-bbq-bingo-moe-s"


def test_free_price():
    assert is_free_price("Free") and is_free_price("FREE admission") and is_free_price("$0")
    assert not is_free_price("$10") and not is_free_price("")


def test_exact_alias_resolves():
    m = r.resolve("Mobile Saenger")
    assert m and m.slug == "saenger-theatre" and m.via == "alias"


def test_fuzzy_alias_resolves_typos_but_not_strangers():
    assert r.resolve("Saenger Theater").slug == "saenger-theatre"
    assert r.resolve("Moe's Orignal BBQ").slug == "moes-bbq"
    assert r.resolve("Soul Kitchen") is None


def test_address_embedded_alias():
    m = r.resolve("", "1905 W 1st St, Gulf Shores, AL 36547")
    assert m and m.slug == "gs-city-hall"


def test_domain_resolution_and_one_hop_origin():
    assert r.resolve("Unknown Hall", url="https://www.mobilesaenger.com/events/123").slug == "saenger-theatre"
    assert r.origin_for_url("https://mobilesaenger.com/x")["slug"] == "saenger-theatre"
    assert r.origin_for_url("https://facebook.com/x") is None


def test_self_promo_detector():
    assert is_self_promoted(["92ZEW", "ZEW"], "Beer BBQ & Bingo with 92ZEW", "Moe's", "")
    assert is_self_promoted(["Mob Mom"], "Fall Fest", "", "The Mob Mom")
    assert not is_self_promoted(["ZEW"], "Zewie the clown", "", "")   # word boundary
    assert not is_self_promoted([], "anything", "", "")
