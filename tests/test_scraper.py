
# aaa
# arrange - przygotuj dane
# act - wywolaj funkcje
# assert - czy git?
# 1 test - 1 metoda, 1 scenariusz (np dobry/zly), kilka assertow
from scraper import Scraper

# tests if proper_link function correctly diagnoses false links:
# (links outside wiki, to files etc.)
def test_proper_link_rejects_invalid_links():
    scraper = Scraper(mode='offline', source='offline_wiki/', phrase="creeper")
    assert not scraper.proper_link('https://minecraft.wiki/')
    assert not scraper.proper_link('https://minecraft.wiki/diamond')
    assert not scraper.proper_link('//w/diamond')
    assert not scraper.proper_link('/w/File:diamond.png')
    assert not scraper.proper_link('#cite_note-19')


def test_proper_link_accepts_valid_links():
    scraper = Scraper(mode='offline', source='offline_wiki/', phrase="creeper")
    assert scraper.proper_link('/w/Skeleton_Horse')
    assert scraper.proper_link('/w/PlayStation_Vita_Edition_1.00')

def test_get_summary_positive_route():
    scraper = Scraper(mode='offline', source='offline_wiki', phrase="creeper")
    proper_result = (
        "A creeper is a common hostile mob that quietly approaches a player, hisses, "
    "and if not retreated from in time, will explode. Creeper explosions can destroy "
    "blocks and deal massive amounts of damage, which can be completely "
    "blocked using a shield."
    )
    assert scraper.get_summary() == proper_result


def test_get_and_clean_article_content_positive_route():
    scraper = Scraper(mode='offline', source='offline_wiki', phrase="creeper")
    text = scraper.get_and_clean_article_content(scraper.get_content_soup())

    # ensure static article elements not present
    assert "View source" not in text
    assert "Wiki discord" not in text
    assert "About Minecraft wiki" not in text

    # ensure symbols not present
    assert "0" not in text
    assert "." not in text
    assert "<head>" not in text
    assert "," not in text

    # ensure proper decapitalisation
    assert "CREEPER" not in text
    assert "Creeper" not in text

    # ensure few certain words are present
    assert "minecraft" in text
    assert "creeper" in text
    assert "a" in text