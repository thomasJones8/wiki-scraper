import requests
import bs4
from bs4 import BeautifulSoup
import io
import re
import os
# lang_confidence_score, wykrest
# gdzeis globalnie ustawic encoding
#TODO: pamietaj o pep8
# czy to porblem ze te funckje robie nieobiektowo?

from wordfreq import word_frequency, top_n_list
from collections import Counter
import json
import pandas as pd
# more convenient format
#pd.options.display.float_format = '{:.6f}'.format
import matplotlib.pyplot as plt
from pathlib import Path

# przyjmowac tez n ?

# TODO: prywatna metoda word counter - tylko wiki czy lang?


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

        # TODO: to samo czyszczenie najpierw co w count words?
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


    def get_and_clean_article_content(self, phrase):
        soup = self.get_content_soup(phrase)
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
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        return text

    # biore tylko to co unikalne dla tego artykulu
    def get_count_words(self, phrase):
        content = Scraper.get_and_clean_article_content(phrase)
        current = Counter(content.split())
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


def generate_chart(df, path):
    path = Path(path)
    # create folders if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # TODO: popracuj jeszcze nad estetyka tego wykresu
    chart = df.plot(kind='bar', figsize=(16, 12), color=['#4c72b0', '#dd8452'],
                    width=1.2, fontsize=21)
    chart.set_title(f'Tyttul do zmiany!!!!', fontsize=22)
    print(chart)

    plt.tight_layout()

    try:
        plt.savefig(path)
    except Exception as e:
        print(f"Encountered exception while trying to save the chart: {e}")
    finally:
        plt.close()


def analyze_relative_word_frequency(mode, n, chart, path):
    lang = "en"  # english
    # get wiki data
    try:
        with open("words-counts.json", "r") as file:
            wiki_data = Counter(json.load(file))
    except FileNotFoundError:
        print("File not found: word_counts.json")
        wiki_data = Counter()
    except json.decoder.JSONDecodeError:
        print("JSON decode error: word_counts.json")
        wiki_data = Counter()

    # get language data

    # To ensure proper comparison, it is neccessary to normalise wiki data
    # lang_data contains probability values [0, 1], meanwhile wiki_data values are
    # numbers of occurences. Simple solution: just divide all wiki_data values by its max
    # (the most often occuring word)

    # normalise
    max_occurences = max(wiki_data.values())
    wiki_data = Counter({k: v / max_occurences for k, v in wiki_data.items()})

    # wersja artykul baza
    if mode == "article":
        df = pd.DataFrame(wiki_data.items(), columns=["word", "wiki_freq"])
        lang_data = Counter({word: word_frequency(word, lang) for word in wiki_data.keys()})
        df["lang_freq"] = df["word"].map(lang_data)
        df = df.sort_values("wiki_freq", ascending=False).head(n).reset_index(drop=True)

    elif mode == "language":
        most_common_words = top_n_list(lang, n)
        # counter: n most common words in the language and their probability
        lang_data = Counter({word: word_frequency(word, lang) for word in most_common_words})
        df = pd.DataFrame(lang_data.items(), columns=["word", "lang_freq"])
        wiki_data = Counter({word: wiki_data[word] for word in lang_data.keys()})
        df["wiki_freq"] = df["word"].map(wiki_data)
        df = df.sort_values("lang_freq", ascending=False).head(n).reset_index(drop=True).set_index("word")



    else:
        print("Unknown mode. Use article or language")

    print(df)
    # merge data - i za pomocą pandas stwórz i wypisz tabelę z
    # kolumnami: word, frequency in the article, frequency in wiki language (słowo, częstotliwość w
    # artykule, częstotliwość w języku wiki)

    # JAK TO JEST Z TYMI 0 I NAN?

    # normalise
    # visualization
    if chart:
        generate_chart(df, path)


def auto_count_words(phrase, depth, wait):
    # Dla każdej przetwarzanej frazy, program powinien:
    # wypisać przetwarzaną frazę,
    print("phrase")
    # pobrać treść artykułu (bez elementów stałych strony)
    text = Scraper.get_and_clean_article_content()
    # jeżeli do obecnej frazy prowadzi sekwencja mniej niż n linków od początkowej frazy,
    #wybrać z niego wszystkie linki prowadzące do innych fraz, których jeszcze nie odwiedził,
    # wykonać --count-words dla przetwarzanej frazy,
    # poczekać t sekund,
    # zrobić to samo dla kolejnej, jeszcze nie przetworzonej frazy.

if __name__ == "__main__":
    scraper = Scraper(mode='online', source='https://minecraft.wiki/')
    #print(scraper.get_table("creeper", 1, False))
    #print("\nyes\n:")
    #print(scraper.get_table("creeper", 1, True))
    #print(scraper.get_table("creeper", 1, False))
    analyze_relative_word_frequency("language", 5, True, "img/test.png")
