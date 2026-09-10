"""
Competitor Price Monitor
-------------------------
Scrapes book listings across 3 categories on books.toscrape.com,
treating each category as a stand-in "competitor store."
Outputs a two-sheet Excel report: raw scraped data + a per-competitor
summary (avg/min/max price, cheapest/priciest item, stock counts).
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests


# --- Configuration ---------------------------------------------------
# Each entry represents one page belonging to one "competitor" category.
main_list = [
    "romance_8",
    "romance_8/page-2.html",
    "science-fiction_16",
    "science_22",
]

# --- Storage lists for scraped fields ---------------------------------
book_detail = []
title__ = []
price__ = []
stock__ = []
source__ = []


# --- Scraping loop ------------------------------------------------------
# Use a single session to reuse the underlying connection across requests
# instead of opening a fresh one each time -- faster, lower overhead.
session = requests.Session()

for page in main_list:
    pages = session.get(f"https://books.toscrape.com/catalogue/category/books/{page}")
    content = BeautifulSoup(pages.content, "html.parser")

    # The listing container holding all book cards on this page
    body = content.find("ol", class_="row")

    # --- Titles ---
    title_cont = body.find_all("h3")
    for title_ in title_cont:
        title = title_.find("a")["title"]
        title__.append(title)

    # --- Prices + stock status ---
    price_body = body.find_all("div", class_="product_price")
    for price_ in price_body:
        # Clean price: strip the currency symbol and convert to float
        price = (price_.find("p", class_="price_color")).text
        price = float(price.replace("£", ""))
        price__.append(price)

        # Normalize stock text into a simple Yes/No flag
        stock = (price_.find("p", class_="instock availability")).text
        if stock.strip() == "In stock":
            stock__.append("Yes")
        else:
            stock__.append("No")

        # Tag this book with which "competitor" (category) it came from.
        # NOTE: order matters here -- "science-fiction" is checked before
        # "science" since "science" is a substring of "science-fiction".
        if "romance" in page:
            source__.append("Romance")
        elif "science-fiction" in page:
            source__.append("Science Fiction")
        elif "science" in page:
            source__.append("Science")


# --- Assemble raw DataFrame ---------------------------------------------
for x in range(len(stock__)):
    bk_det = {"Title": title__[x], "Price": price__[x], "Stock Status": stock__[x]}
    book_detail.append(bk_det)

df = pd.DataFrame(book_detail)
df["Source"] = source__


# --- Build summary table: one row per competitor -------------------------

# Average / min / max price per competitor
df2 = df.groupby("Source")["Price"].agg(
    **{"Avg Price": "mean", "Min Price": "min", "Max Price": "max"}
).reset_index()

# Cheapest item's title per competitor
cheapest = (
    df.loc[df.groupby("Source")["Price"].idxmin()][["Source", "Title"]]
    .rename(columns={"Title": "Cheapest Title"})
)
df2 = df2.merge(cheapest, on="Source")

# Priciest item's title per competitor
priciest = (
    df.loc[df.groupby("Source")["Price"].idxmax()][["Source", "Title"]]
    .rename(columns={"Title": "Priciest Title"})
)
df2 = df2.merge(priciest, on="Source")

# In-stock / out-of-stock counts per competitor
stock_counts = (
    df.groupby("Source")["Stock Status"]
    .value_counts()
    .unstack(fill_value=0)
    .reset_index()
    .rename(columns={"Yes": "In Stock Count", "No": "Out of Stock Count"})
)
df2 = df2.merge(stock_counts, on="Source")


# --- Export: two-sheet Excel report --------------------------------------
with pd.ExcelWriter("price_report.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="raw_data", index=False)
    df2.to_excel(writer, sheet_name="summary", index=False)

print("Report saved to price_report.xlsx")
