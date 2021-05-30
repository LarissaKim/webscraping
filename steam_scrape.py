import re

from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen

# URL for Steam's Oculus Rift VR category
html = urlopen('https://store.steampowered.com/search/?vrsupport=102').read()
bs = BeautifulSoup(html, 'html.parser')

titles = [title.get_text() for title in bs.findAll("span",
                                                   {"class": "title"})]

release_dates = [date.get_text()
                 for date in bs.findAll(
            "div", {"class": "col search_released responsive_secondrow"})]

app_prices = bs.findAll(
        "div", {"class":
                    ["col search_price responsive_secondrow",
                     "col search_price discounted responsive_secondrow"]})
for price in app_prices:
    # Remove the non-sale price of an app if it is on sale
    for strike in price.select("strike"):
        strike.extract()
prices = [price.get_text() for price in app_prices]
# Remove unnecessary whitespace from string
prices = [(re.sub(r"^\s+|\s+$", '', price)) for price in prices]

discounts = [discount.get_text()
             for discount in bs.findAll("div",
                                        {"class": "col search_discount "
                                                  "responsive_secondrow"})]
# Remove unnecessary whitespace from string
discounts = [(re.sub(r"[^(?:\-\d+%)]", '', discount))
             for discount in discounts]

review_summary_container = bs.findAll("span",
                                      {"class": "search_review_summary"})
review_summaries = [summary.get('data-tooltip-html')
                    for summary in review_summary_container]
# Only keep user review rating level (happens before <br>)
review_summaries = [(re.findall(r"(.*?)(?=<)", summary)[0])
                    for summary in review_summaries]

# Get only app links
links = [link.get("href")
         for link in bs.find('div', {'id': 'search_resultsRows'})
             .find_all('a', {'href': re.compile(r'(.com/app/\d+/)')})]

output = []
for info in zip(titles, release_dates, prices,
                discounts, review_summaries, links):
    resp = {'title': info[0],
            'release_date': info[1],
            'price': info[2],
            'discount': info[3],
            'review_summary': info[4],
            'link': info[5]}
    output.append(resp)

df = pd.DataFrame(output)
df.to_excel('steam_scrape.xlsx')
