# tworzenie scrapera, printy, argparsownaie
# tutaj if name main
# manager - scraper.py -

#TODO: obsluzyc bledne wywolania np? np table bez numeru
import argparse
import time
from codecs import namereplace_errors
from collections import Counter

import pandas as pd
from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray

from scraper import Scraper
from analyzer import DataAnalyzer


class Manager:
    def __init__(self, mode='online', source='https://minecraft.wiki/w/', lang='en',
                 word_counts_path='word-counts.json'):
        #TODO: dodac guardy?
        self.analyzer = DataAnalyzer(lang=lang, word_counts_path=word_counts_path)
        self.parser = self.setup_parser()
        self.mode = mode
        self.source = source

    @staticmethod
    def get_table_statistics(table):
        values_list = table.values.flatten()
        return pd.Series(values_list).value_counts().reset_index()

    def run(self):
        parser = self.parser
        analyzer = self.analyzer

        args = parser.parse_args()



        if args.summary:
            scraper = Scraper(mode=self.mode, source=self.source, phrase=args.summary)
            print(scraper.get_summary())
        elif args.table:
            scraper = Scraper(mode=self.mode, source=self.source, phrase=args.table)
            phrase = args.table
            table = scraper.get_table(args.number, args.first_row_is_header)
            print(table)
            if table is not None:
                table.to_csv(phrase.strip().replace(" ", "_") + ".csv")
                print(Manager.get_table_statistics(table))

        elif args.count_words:
            scraper = Scraper(mode=self.mode, source=self.source, phrase=args.count_words)
            soup = scraper.get_content_soup()
            cleaned_text = scraper.get_and_clean_article_content(soup)
            analyzer.update_word_counts(cleaned_text)
        elif args.analyze_relative_word_frequency:
            df = analyzer.analyze_relative_word_frequency(args.mode, args.count)
            if args.chart:
                chart = analyzer.generate_chart(df, args.chart)
        elif args.auto_count_words:
            self.auto_count_words(args.auto_count_words, args.depth, args.wait, set())



    @staticmethod
    def setup_parser():
        #TODO: uzupelnij helpy

        parser = argparse.ArgumentParser("Wiki Scraper parser")
        commands = parser.add_mutually_exclusive_group(required=True)
        commands.add_argument("--summary", type=str, help="summary of the article.")
        commands.add_argument("--table", type=str, help="")
        commands.add_argument("--count-words", type=str, help="")
        commands.add_argument("--analyze-relative-word-frequency", action="store_true", help="")
        commands.add_argument("--auto-count-words", type=str, help="")

        # optional arguments
        parser.add_argument("--number", type=int, help="")
        parser.add_argument("--first-row-is-header", action="store_true", help="")
        parser.add_argument("--mode",type=str, choices=["article", "language"], help="")
        parser.add_argument("--count",type=int, help="")
        parser.add_argument("--chart", type=str, help="")
        parser.add_argument("--depth",type=int, help="")
        parser.add_argument("--wait",type=int, help="")

        return parser


    # wolac z pustym setem
    # TODO: ktorych jeszcze nie odwiedzil!!!
    # calling count_words on an article, articles referenced by it etc. depth times using DFS
    def auto_count_words(self, phrase, depth, wait, already_met):
        if phrase in already_met:
            return
        already_met.add(phrase)
        scraper = Scraper(mode=self.mode, source=self.source, phrase=phrase)
        analyzer = self.analyzer
        print(phrase)

        soup = scraper.get_content_soup(phrase)
        cleaned_text = scraper.get_and_clean_article_content(soup)
        # wykonać --count-words dla przetwarzanej frazy,
        analyzer.update_word_counts(cleaned_text)

        # jeżeli do obecnej frazy prowadzi sekwencja mniej niż n linków od początkowej frazy,
        # wybrać z niego wszystkie linki prowadzące do innych fraz, których jeszcze nie odwiedził,
        if depth > 0:
            # wolac z --depth - anie bo to pythonc
            # wyciagnij linki
            # tu drugi raz pobieram strone - pytanie na ile to problem
            phrases = scraper.get_referenced_phrases(phrase)
            # na wszelki poczekaj
            for phrase in phrases:
                # wait (to bypass wiki security)
                time.sleep(1)
                #
                self.auto_count_words(phrase, depth - 1, wait, already_met)



if __name__ == "__main__":
    manager = Manager()
    manager.run()
