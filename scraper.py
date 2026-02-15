import io
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


class Scraper:
    """
    a class responsible for accessing data from wiki
    1 object = 1 article
    mode: online (from website) / offline (from file)
    source: base address/file path
    https://minecraft.wiki/w/
    nazwa_folderu/
    """

    def __init__(self, phrase, mode="online", source="https://minecraft.wiki/"):
        # more convenient format of printing number in pandas
        pd.options.display.float_format = '{:.6f}'.format

        if mode not in ['online', 'offline']:
            raise ValueError('Invalid mode. Options: online, offline')
        self.mode = mode
        self.source = source
        self.phrase = phrase

    def get_content_soup(self):
        """
         returns the important part of the source code (html) of the article
         type tag (beautifulsoup)
        """
        if not self.source.endswith("/"):
            self.source += "/"
        path = self.source + self.phrase.strip().replace(" ", "_")
        if self.mode == "offline":
            if not path.endswith(".html"):
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
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print("HTTP error - the article does not exist")
                return None
            response.encoding = "utf-8"
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        # part of html containing all needed content
        content = soup.find(id="mw-content-text")
        if not content:
            print("Content not found")
            return None
        return content

    def get_summary(self):
        soup = self.get_content_soup()
        if not soup:
            print("get_html failed")
            return None
        # skipping the infobox to reach the actual text
        infobox = soup.find(class_="infobox")
        if infobox:
            infobox.decompose()

        # skip emtpy paragraphs
        paragraphs = soup.find_all('p')

        if not paragraphs:
            print("Finding paragraphs failed")
            return None

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True, separator=" ")
            if len(text) > 0:
                break

        if (len(text) == 0):
            print("All paragraphs have length 0")
            return None

        # the separator above creates spaces before punctuation marks
        # using regex to fix it
        text = re.sub(r"\s+([.,!?;:])", r'\1', text)
        return text.replace(" -", "-")

    def get_table(self, number, is_first_row_header):
        if is_first_row_header:
            header = 0
        else:
            header = None

        soup = self.get_content_soup()
        if not soup:
            print("get_html failed")
            return None
        try:
            tables = pd.read_html(io.StringIO(str(soup)), header=header, index_col=0)
        except ValueError:
            print("No tables found")
            return None

        if number < 1 or len(tables) < number:
            print(f"Number out of range [1, {len(tables)}*]")
            print("*number of tables in the article")
            return None

        table = tables[number - 1]
        return table

    @staticmethod
    def get_and_clean_article_content(soup):
        """
        returns only the text part of the article, without numbers
        and symbols, to ensure proper count_words work
        """
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
        # get rid of everything except unicode letters
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"[\d_]", " ", text)

        return text

    @staticmethod
    def proper_link(link):
        """
        checks proper links for auto_count_words
        receives links in this format (ex.) - /w/Banner_Pattern
        """

        # outside wiki or inside the specific article link (#...)
        if not link.startswith("/w/"):
            return False
        # symbols indicating wrong links:
        #  ":" - files
        if ":" in link:
            return False
        return True

    @staticmethod
    def get_referenced_phrases(soup):
        if not soup:
            print("get_referenced_phrases received an empty set")
            return set()

        # get all links from anchors
        links = {str(a["href"]) for a in soup.find_all("a", href=True)}

        # exclude improper links (outside wiki, links to files)
        # using set to visit only once multiply referenced sites
        proper_links = {link for link in links if Scraper.proper_link(link)}

        # clean:
        # 1. get rid of "/w/" prefix
        # 2. get rid of links to specific part of an article (ex.: https://minecraft.wiki/w/Advancement#A_Throwaway_Joke)
        phrases = {link.split("/")[2].split("#")[0] for link in proper_links}
        return phrases
