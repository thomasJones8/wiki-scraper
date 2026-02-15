import pytest

# aaa
# arrange - przygotuj dane
# act - wywolaj funkcje
# assert - czy git?
# 1 test - 1 metoda, 1 scenariusz (np dobry/zly), kilka assertow
from scraper import Scraper

# tests if proper_link function correctly diagnoses false links:
# (links outside wiki, to files etc.)
def test_proper_link_rejects_invalid_links():
    assert not Scraper.proper_link('https://minecraft.wiki/')
    assert not Scraper.proper_link('https://minecraft.wiki/diamond')
    assert not Scraper.proper_link('//w/diamond')
    assert not Scraper.proper_link('/w/File:diamond.png')
    assert not Scraper.proper_link('#cite_note-19')


def test_proper_link_accepts_valid_links():
    assert Scraper.proper_link('/w/Skeleton_Horse')
    assert Scraper.proper_link('/w/PlayStation_Vita_Edition_1.00')

def test_scraper_properly_rejects_nonexistent_file():
    scraper = Scraper(mode='offline', source='offline_wiki', phrase="SpectreFileNOTexisting")
    result = scraper.get_content_soup()
    assert result is None, "Scraper should return None for non-existent file"

def test_get_and_clean_article_content_positive_route():
    scraper = Scraper(mode='offline', source='offline_wiki', phrase="creeper")
    text = scraper.get_and_clean_article_content(scraper.get_content_soup())

    # ensure static article elements not present
    assert "view source" not in text
    assert "wiki discord" not in text
    assert "about minecraft wiki" not in text

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