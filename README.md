# WikiScraper & NLP Analyzer

A Python CLI application for automated data extraction, BFS web crawling, and NLP-based language analysis of the Minecraft Wiki. 

Built with a modular, object-oriented architecture, the tool handles HTML parsing to extract clean text and tabular data, performs automated graph traversal across wiki links with rate-limiting, and features a data science module. The analytical part evaluates a custom `lang_confidence_score` to detect the language of an article based on relative word frequencies compared to general language corpora.

*Note: This tool was designed specifically for and tested on [https://minecraft.wiki/](https://minecraft.wiki/). While it interacts with the MediaWiki engine, it may require structural adjustments to work correctly on other wiki domains due to differences in custom HTML templates.*

### 🎓 Academic Context & Achievements
This project was developed as a final assignment for the Python Course (3rd semester, Computer Science) at the MIMUW faculty.

The project received the **maximum possible grade** for both the implementation and the technical defense. The defense involved proving a deep, comprehensive understanding of the codebase, explaining the underlying algorithms, and successfully implementing live modifications to the code in front of the professor. For detailed academic requirements (in Polish), see [SPECIFICATION_PL.md](SPECIFICATION_PL.md).

### Tech Stack
* **Language:** Python
* **Web Scraping:** BeautifulSoup4, requests
* **Data Processing & NLP:** pandas, wordfreq
* **Data Visualization:** matplotlib, Jupyter Notebook
* **Testing:** `unittest` 

### Project Structure
* **wiki_scraper.py** - The main CLI entry point handling argument parsing.
* **scraper.py** - Core scraping engine containing HTML parsing logic and the BFS crawler.
* **analyzer.py** - Data analysis module responsible for word frequency calculations, plotting, and language detection.
* **analysis.ipynb** - A Jupyter Notebook containing empirical research and visualizations evaluating the effectiveness of the `lang_confidence_score` metric across different languages and $k$ values.
* **test_scraper.py** - Offline unit tests using local HTML mocks to verify parsing logic without network calls.
* **wiki_scraper_integration_test.py** - End-to-end integration test verifying the core summary extraction pipeline.

### CLI Usage

The tool is executed via the command line and supports several independent operations:

**1. Article Summary Extraction**
Extracts the first paragraph of a given wiki article, stripping all HTML tags.
    python wiki_scraper.py --summary "Enderman"

**2. Tabular Data Extraction**
Locates the n-th `<table>` on the page, calculates value frequencies, and exports the parsed dataset to a `.csv` file.
    python wiki_scraper.py --table "Type" --number 2 --first-row-is-header

**3. Word Frequency Aggregation**
Counts all words in the article's core text and updates a persistent JSON dictionary (`word-counts.json`).
    python wiki_scraper.py --count-words "Enderman"

**4. Comparative Language Analysis**
Compares scraped word frequencies against general statistical frequencies of the host language. Generates a normalized pandas dataframe and a matplotlib bar chart.
    python wiki_scraper.py --analyze-relative-word-frequency --mode "article" --count 10 --chart "output.png"

**5. Automated Web Crawling**
Explores the wiki's link graph starting from a base article using Breadth-First Search (BFS) up to a specified depth. Implements rate limiting (`--wait`).
    python wiki_scraper.py --auto-count-words "Enderman" --depth 3 --wait 1

### Testing Strategy
The architecture emphasizes offline testability. The `WikiScraper` class can be initialized with local HTML files instead of live URLs (`use_local_html_file_instead=True`), allowing for fast, deterministic unit testing (`test_scraper.py`) without risking IP bans or relying on network stability.

### Installation

1. Clone the repository and navigate to the project directory:
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name

2. Create and activate a virtual environment:
    # Windows:
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

3. Install the required dependencies:
    pip install -r requirements.txt
