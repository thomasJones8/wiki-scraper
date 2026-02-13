# tworzenie scrapera, printy, argparsownaie
# tutaj if name main

#TODO: przy obsludze get table oblsluz tu print i zapis do csv
import argparse
import time
import pandas as pd
from scraper import Scraper
from analyzer import DataAnalyzer


class Manager:
    def __init__(self, mode='online', source='https://minecraft.wiki/w/', lang='en',
                 word_counts_path='word-counts.json'):
        self.scraper = Scraper(mode=mode, source=source)
        self.analyzer = DataAnalyzer(lang=lang, word_counts_path=word_counts_path)
        self.parser = self.setup_parser()

    @staticmethod
    def setup_parser():
        #TODO: uzupelnij helpy

        parser = argparse.ArgumentParser("Wiki Scraper parser")
        commands = parser.add_mutually_exclusive_group(required=True)
        commands.add_argument("--summary", type="str", help="summary of the article.")
        commands.add_argument("--table", type="str", help="")
        commands.add_argument("--count-words", type="str", help="")
        commands.add_argument("--analyze-relative-word-frequency", action="store_true", help="")
        commands.add_argument("--auto-count-words", type="str", help="")

        # optional arguments
        parser.add_argument("--number", type=int, help="")
        parser.add_argument("--first-row-is-header", action="store_true", help="")
        parser.add_argument("--mode",type=str, choices=["article", "language"], help="")
        parser.add_argument("--count",type=int, help="")
        parser.add_argument("--chart", type=str, help="")
        parser.add_argument("--depth",type=int, help="")
        parser.add_argument("--wait",type=int, help="")

        return parser



    # TODO: ktorych jeszcze nie odwiedzil!!!
    # calling count_words on an article, articles referenced by it etc. depth times using DFS
    def auto_count_words(self, phrase, depth, wait):
        print(phrase)

        soup = self.get_content_soup(phrase)
        cleaned_text = self.get_and_clean_article_content(soup)
        # wykonać --count-words dla przetwarzanej frazy,
        self.get_count_words(cleaned_text)

        # jeżeli do obecnej frazy prowadzi sekwencja mniej niż n linków od początkowej frazy,
        # wybrać z niego wszystkie linki prowadzące do innych fraz, których jeszcze nie odwiedził,
        if depth > 0:
            # wolac z --depth - anie bo to pythonc
            # wyciagnij linki
            # tu drugi raz pobieram strone - pytanie na ile to problem
            phrases = self.get_referenced_phrases(phrase)
            # na wszelki poczekaj
            for phrase in phrases:
                # wait (to bypass wiki security)
                time.sleep(1)
                #
                self.auto_count_words(phrase, depth - 1, wait)


#table
# table.to_csv(phrase.strip().replace(" ", "_") + ".csv")        # tu musze te pandasowe rzeczy zrobic
#
#         # statistics
#         list = table.values.flatten()
#         print(pd.Series(list).value_counts().reset_index())