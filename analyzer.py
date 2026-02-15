import json
import os
from pathlib import Path
import pandas as pd
from collections import Counter
from matplotlib import pyplot as plt
from wordfreq import word_frequency, top_n_list


class DataAnalyzer:
    def __init__(self, lang="en", word_counts_path="word-counts.json"):
        self.lang = lang
        self.word_counts_path = word_counts_path

    def update_word_counts(self, cleaned_text):
        current = Counter(cleaned_text.split())
        path = self.word_counts_path

        # counting started already
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                old = Counter(json.load(file))
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
            with open(word_counts, "r", encoding="utf-8") as file:
                wiki_data = json.load(file)
        except FileNotFoundError:
            print(f"File not found: {word_counts}")
            wiki_data = {}
        except json.decoder.JSONDecodeError:
            print(f"JSON decode error: {word_counts}")
            wiki_data = {}

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
        wiki_data = {k: v / max_occurences for k, v in wiki_data.items()}
        # for lang normalisation later
        lang_top_frequency = word_frequency(top_n_list(lang, 1)[0], lang)

        if mode == "article":
            df = pd.DataFrame(wiki_data.items(), columns=["word", "wiki_freq"])
            df = df.sort_values("wiki_freq", ascending=False).head(n).reset_index(drop=True)
            # instantly normalising
            lang_data = {word: word_frequency(word, lang) / lang_top_frequency for word in df["word"]}
            df["lang_freq"] = df["word"].map(lang_data).replace(0.0, float('nan'))

        elif mode == "language":
            most_common_words = top_n_list(lang, n)
            # counter: n most common word in the language and their probability
            # instantly normalising
            lang_data = {word: word_frequency(word, lang) / lang_top_frequency for word in most_common_words}
            df = pd.DataFrame(lang_data.items(), columns=["word", "lang_freq"])
            df["wiki_freq"] = df["word"].map(wiki_data).replace(0.0, float('nan'))
            df = df.sort_values("lang_freq", ascending=False).head(n).reset_index(drop=True)

        else:
            print("Unknown mode. Use 'article' or 'language'")
            return pd.DataFrame()

        # renaming to comply with requirements
        df = df.rename(columns={
            "wiki_freq": "frequency in the article",
            "lang_freq": "frequency in wiki language"
        })

        # ensure required order
        df = df[["word", "frequency in the article", "frequency in wiki language"]]

        return df

    @staticmethod
    def generate_chart(df, path):
        path = Path(path)
        # create folders if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        chart = df.plot(kind='bar', x="word", figsize=(16, 10), color=['#4c72b0', '#dd8452'],
                        width=0.8, fontsize=16, edgecolor="black")
        chart.set_title(f'Word frequency: wiki vs language', fontsize=24, pad=20)
        chart.set_ylabel('Frequency (normalised)', fontsize=18)
        chart.set_xlabel('Word', fontsize=18)
        chart.legend(fontsize=16)
        plt.xticks(rotation=45, ha='right')
        chart.grid(axis='y', linestyle='--', alpha=0.7)
        chart.set_axisbelow(True)
        plt.tight_layout()

        try:
            plt.savefig(path)
        except Exception as e:
            print(f"Encountered exception while trying to save the chart: {e}")
        finally:
            plt.close()
