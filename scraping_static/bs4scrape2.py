from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

# Full catalog: 50 pages, ~20 books per page = ~1000 books total.
# Used here to test whether the scraping pipeline actually holds up
# at real scale, before promising "up to 100 pages" on a live gig.

total_pages = 50
book_detail = []
title__ = []
price__ = []
stock__ = []
page_no__ = []

session = requests.Session()

for page_num in range(1, total_pages + 1):
    url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
    pages = session.get(url)

    # If a page fails to load, note it and keep going instead of
    # crashing the whole run partway through -- important at this scale.
    if pages.status_code != 200:
        print(f"Page {page_num} failed with status {pages.status_code}")
        continue

    content = BeautifulSoup(pages.content, "html.parser")
    body = content.find("ol", class_="row")

    title_cont = body.find_all("h3")
    for title_ in title_cont:
        title = title_.find("a")["title"]
        title__.append(title)
        page_no__.append(page_num)

    price_body = body.find_all("div", class_="product_price")
    for price_ in price_body:
        price = (price_.find("p", class_="price_color")).text
        price = float(price.replace("£", ""))
        price__.append(price)

        stock = (price_.find("p", class_="instock availability")).text
        if stock.strip() == "In stock":
            stock__.append("Yes")
        else:
            stock__.append("No")

    # Small delay between requests -- polite scraping, avoids hammering
    # the server and getting rate-limited/blocked mid-run.
    time.sleep(0.3)

    if page_num % 10 == 0:
        print(f"Completed page {page_num}/{total_pages}")

for x in range(len(title__)):
    bk_det = {"Title": title__[x], "Price": price__[x], "Stock Status": stock__[x], "Page": page_no__[x]}
    book_detail.append(bk_det)

df = pd.DataFrame(book_detail)

print(f"\nTotal books scraped: {len(df)}")
print(f"Expected (per site): ~1000")

df.to_excel("full_catalog_test.xlsx", index=False)
print("Saved to full_catalog_test.xlsx")