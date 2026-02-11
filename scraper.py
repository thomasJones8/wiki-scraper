import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import io
import re
import json
import os
from collections import Counter





# printowac tylko w wikiscaper?
#dostaje sparsowane parametry linii poleceni

class Scraper(object):
    #mode: online (from website) / offline (from file)
    #source: base address/file path

    #https://minecraft.wiki/w/
    #nazwa_folderu/
    def __init__(self, mode, source):
        if mode not in ['online', 'offline']:
            raise ValueError('Invalid mode. Options: online, offline')
        self.mode = mode
        self.source = source

    # returns the important part of the source code (html) of the article
    # type tag (beautifulsoup)
    def get_content_soup(self, phrase):
        #TODO: zmien na uzycie urllib.parse.urljoin
        path = self.source + phrase.strip().replace(" ", "_")
        if self.mode == "offline":
            path += ".html"
            try:
                with open(path, "r", encoding="utf-8") as file:
                    html = file.read()
            except FileNotFoundError:
                print("File not found")
                return None
        else:
            # works without fake user agent
            response = requests.get(path)
            # throws exception in case of website access problems
            response.raise_for_status()
            response.encoding = "utf-8"
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        # part of html containing all needed content
        content = soup.find(id="mw-content-text")
        if not content:
            print("Content not found")
            return None
        return content

    def get_summary(self, phrase):
        soup = self.get_content_soup(phrase)
        if not soup:
            print("get_html failed")
            return None
        # skiping the infobox to reach the actual text
        infobox = soup.find(class_="infobox")
        if infobox:
            infobox.decompose()

        paragraph = soup.find('p')
        if not paragraph:
            print("Finding first paragraph failed")
            return None
        # czemy mi ciagle podkresla te separatory???
        text = paragraph.get_text(strip= True, separator=" ")
        # the separator above creates spaces before punctuation marks
        # using regex to fix it
        text = re.sub(r"\s+([.,!?;:])", r'\1' ,text)
        return text

# zwraca tabele (dataframe)
# czy ta funckja ma omijac bezsnesowne tabele
    def get_table(self, phrase, number, is_first_row_header):
        #wybastrahowac wyzej te funkcje
        if is_first_row_header:
            header = 0
        else:
            header = None

        soup = self.get_content_soup(phrase)
        if not soup:
            print("get_html failed")
            return None
        try:
            tables =  pd.read_html(io.StringIO(str(soup)), header=header, index_col=0)
        except ValueError:
            print("No tables found")
            return None

        if number < 1 or len(tables) < number:
            print("Number out of range [1, number of tables]")
            return None

        table = tables[number - 1]
        return table


    # biore tylko to co unikalne dla tego artykulu
    def get_count_words(self, phrase):
        soup =  self.get_content_soup(phrase)
        if not soup:
            print("get_html failed")
            return None

        # unwanted elements - menu, links, css etc.
        blacklist = [
            "script",
            "style",
            ".navbox",
            ".mw-editsection",
            ".toc",
            ".reflist",
            ".printfooter",
            ".history-json",
            "sup",
            ".references",
            ".mw-cite-backlink",
            ".external"

        ]

        # removing unwanted elements
        for selector in blacklist:
            tags = soup.select(selector)
            for element in tags:
                element.decompose()

        # preparing the text for analysis - converting to lowercase, removing numbers and symbols
        text = soup.get_text(separator=" ").lower()
        text = re.sub(r"[^a-zA-Z\s]", " " , text)
        current = Counter(text.split())

        path = "words-counts.json"

        # counting started already
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                old = Counter(json.loads(file.read()))
            # update
            new = old + current
        # starting counting
        else:
            new = current
        # save result
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(new, indent=4))


if __name__ == "__main__":
    scraper = Scraper(mode='online', source='https://minecraft.wiki/')
    print(scraper.get_count_words("creeper"))
    #print(scraper.get_table("creeper", 1, False))