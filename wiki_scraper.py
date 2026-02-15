# tworzenie scrapera, printy, argparsownaie
# tutaj if name main
# manager - scraper.py -

import argparse
import time
import pandas as pd

from scraper import Scraper
from analyzer import DataAnalyzer


class Manager:
    def __init__(self, mode='online', source='https://minecraft.wiki/w/', lang='en',
                 word_counts_path='word-counts.json'):
        #TODO: dodac guardy?
        self.analyzer = DataAnalyzer(lang=lang, word_counts_path=word_counts_path)
        self.mode = mode
        self.source = source

    @staticmethod
    def get_table_statistics(table):
        values_list = table.values.flatten()
        return pd.Series(values_list).value_counts().reset_index()



    def summary(self, phrase):
        scraper = Scraper(mode=self.mode, source=self.source, phrase=phrase)
        print(scraper.get_summary())

    def table(self, phrase, number, first_row_is_header):
        scraper = Scraper(mode=self.mode, source=self.source, phrase=phrase)
        table = scraper.get_table(number, first_row_is_header)
        if table is not None:
            print(table)
            table.to_csv(phrase.strip().replace(" ", "_") + ".csv")
            print(Manager.get_table_statistics(table))

    def count_words(self, phrase):
        scraper = Scraper(mode=self.mode, source=self.source, phrase=phrase)
        soup = scraper.get_content_soup()
        cleaned_text = scraper.get_and_clean_article_content(soup)
        self.analyzer.update_word_counts(cleaned_text)

    def analyze_relative_word_frequency(self, mode, count):
        df = self.analyzer.analyze_relative_word_frequency(mode, count)
        print(df)
        return df


    # wolac z pustym setem
    # calling count_words on an article, articles referenced by it etc. depth times using DFS
    def auto_count_words(self, phrase, depth, wait, already_met):
        if phrase in already_met:
            return
        already_met.add(phrase)
        scraper = Scraper(mode=self.mode, source=self.source, phrase=phrase)
        analyzer = self.analyzer
        print(phrase)

        soup = scraper.get_content_soup()
        cleaned_text = scraper.get_and_clean_article_content(soup)
        # wykonać --count-words dla przetwarzanej frazy,
        analyzer.update_word_counts(cleaned_text)

        # jeżeli do obecnej frazy prowadzi sekwencja mniej niż n linków od początkowej frazy,
        # wybrać z niego wszystkie linki prowadzące do innych fraz, których jeszcze nie odwiedził,
        if depth > 0:
            # wyciagnij linki
            phrases = scraper.get_referenced_phrases(soup)
            # na wszelki poczekaj
            for phrase in phrases:
                # wait (to bypass wiki security)
                time.sleep(1)
                #
                self.auto_count_words(phrase, depth - 1, wait, already_met)



def setup_parser():
    #TODO: uzupelnij helpy

    parser = argparse.ArgumentParser("Wiki Scraper parser")
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--summary", type=str)
    commands.add_argument("--table", type=str)
    commands.add_argument("--count-words", type=str)
    commands.add_argument("--analyze-relative-word-frequency", action="store_true")
    commands.add_argument("--auto-count-words", type=str)

    # optional arguments
    parser.add_argument("--number", type=int)
    parser.add_argument("--first-row-is-header", action="store_true")
    parser.add_argument("--mode",type=str, choices=["article", "language"])
    parser.add_argument("--count",type=int)
    parser.add_argument("--chart", type=str)
    parser.add_argument("--depth",type=int)
    parser.add_argument("--wait",type=int)

    return parser

if __name__ == "__main__":
    manager = Manager()
    parser = setup_parser()
    args = parser.parse_args()

    # tu parsowanie
    if args.summary:
        manager.summary(args.summary)
    elif args.table:
        if args.number is None:
            print("No number is specified. Usage: --table \"phrase\" --number n [--first-row-is-header]")
        else:
            manager.table(phrase=args.table, number=args.number,
                      first_row_is_header=args.first_row_is_header)
    elif args.count_words:
        manager.count_words(args.count_words)
    elif args.analyze_relative_word_frequency:
        if args.mode is None or args.count is None:
            print(
                "Usage: --analyze-relative-word-frequency --mode 'mode' --count n"
            "[--chart 'file_path']")
        else:
            df = manager.analyze_relative_word_frequency(mode=args.mode, count=args.count)
            if args.chart:
                manager.analyzer.generate_chart(df, args.chart)
    elif args.auto_count_words:
        if args.depth is None or args.wait is None:
            print("Usage: --auto-count-words 'phrase' --depth n --wait t")
        else:
            manager.auto_count_words(args.auto_count_words, args.depth, args.wait, set())
