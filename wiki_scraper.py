# tworzenie scrapera, printy, argparsownaie




#table
# table.to_csv(phrase.strip().replace(" ", "_") + ".csv")        # tu musze te pandasowe rzeczy zrobic
#
#         # statistics
#         list = table.values.flatten()
#         print(pd.Series(list).value_counts().reset_index())


# mutually exlsuivy group albo po prostu luzniej - ify

import argparse

parser = argparse.ArgumentParser("Wiki Scraper parser")

subparsers = parser.add_subparsers(help="Wiki Scraper commands")

parser_summary = subparsers.add_parser("--summary", help="First paragraph of article's text")
parser_summary.add_argument("phrase", help="First paragraph of article's text")



# parsowanie

args = parser.parse_args()

if args.
