# Portfolio Projects

Python-based data automation — web scraping, cleaning, and reporting.

---

## Competitor Price Monitor

Scrapes product listings across multiple sources, cleans and structures the data, and outputs a two-sheet Excel report: raw data plus a per-source summary (average/min/max price, cheapest and priciest items, stock counts).

**Tech used:** Python, `requests`, `BeautifulSoup`, `pandas`, `openpyxl`

**What it demonstrates:**
- Scraping structured data from live static HTML pages
- Cleaning messy real-world data (currency symbols, inconsistent formatting)
- Aggregating and comparing data across multiple sources with `pandas.groupby`
- Exporting clean, multi-sheet, client-ready Excel reports

**Sample output:** [`price_report.xlsx`](./price_report.xlsx)

Also includes [`full_catalog_test.xlsx`](./full_catalog_test.xlsx) — a scale test run against a 50-page, ~1000-item catalog to confirm the scraper handles larger jobs reliably, not just small samples.

---

## About

Built as part of a freelance automation service — I help businesses turn messy or scattered data into clean, usable reports. Available for hire on Fiverr.
