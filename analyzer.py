import json
import os
from collections import Counter
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from wordfreq import word_frequency, top_n_list


# tu nas nie obchodzi html?


class DataAnalyzer:
    def __init__(self, lang="en", word_counts_path="word-counts.json"):
        self.lang = lang
        self.word_counts_path = word_counts_path

    # biore tylko to co unikalne dla tego artykulu
    # TODO: PAMIETAJ ZE TO DOSTAJE INPUT NIE Z GET CONTENT TYLKO Z GET CLEANED TEXT
    def update_word_counts(self, cleaned_text):
        current = Counter(cleaned_text.split())
        path = self.word_counts_path

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



    def analyze_relative_word_frequency(self, mode, n):
        lang = self.lang
        word_counts = self.word_counts_path
        # get wiki data
        try:
            with open(word_counts, "r") as file:
                wiki_data = Counter(json.load(file))
        except FileNotFoundError:
            print(f"File not found: {word_counts}")
            wiki_data = Counter()
        except json.decoder.JSONDecodeError:
            print(f"JSON decode error: {word_counts}")
            wiki_data = Counter()

        if not wiki_data:
            print(f"{word_counts} is empty - no data to analyze")
            return None

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
            most_common_word = top_n_list(lang, n)
            # counter: n most common word in the language and their probability
            lang_data = Counter({word: word_frequency(word, lang) for word in most_common_word})
            df = pd.DataFrame(lang_data.items(), columns=["word", "lang_freq"])
            wiki_data = Counter({word: wiki_data[word] for word in lang_data.keys()})
            df["wiki_freq"] = df["word"].map(wiki_data)
            df = df.sort_values("lang_freq", ascending=False).head(n).reset_index(drop=True)

        else:
            print("Unknown mode. Use article or language")
            return pd.DataFrame()

        # merge data - i za pomocą pandas stwórz i wypisz tabelę z
        # kolumnami: word, frequency in the article, frequency in wiki language (słowo, częstotliwość w
        # artykule, częstotliwość w języku wiki)

        # JAK TO JEST Z TYMI 0 I NAN?

        # renaming to comply with requirements
        df = df.rename(columns={
            "wiki_freq": "frequency in the article",
            "lang_freq": "frequency in wiki language"
        })
        # normalise


        return df
    # TODO: co dokladnie mam zrobic z chart?


    @staticmethod
    def generate_chart(df, path):
        path = Path(path)
        # create folders if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: popracuj jeszcze nad estetyka tego wykresu
        chart = df.plot(kind='bar', x="word", figsize=(16, 12), color=['#4c72b0', '#dd8452'],
                        width=1.2, fontsize=21)
        chart.set_title(f'Word frequency: wiki vs language', fontsize=22)

        plt.tight_layout()

        try:
            plt.savefig(path)
        except Exception as e:
            print(f"Encountered exception while trying to save the chart: {e}")
        finally:
            plt.close()
