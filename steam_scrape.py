from dateutil import parser
import re
from time import strftime
from urllib.request import urlopen

from bs4 import BeautifulSoup
import pandas as pd

# URL for Steam's Oculus Rift VR category sorted by relevance (default)
# Page loads 50 results (Note: This code can't handle recently released
# games with no reviews, yet)
html = urlopen('https://store.steampowered.com/search/?vrsupport=102').read()
bs = BeautifulSoup(html, 'html.parser')

app_titles = [title.get_text() for title in bs.findAll("span",
                                                       {"class": "title"})]

dates = [date.get_text() for date in bs.findAll(
        "div", {"class": "search_released"})]
dates = [parser.parse(date) for date in dates]

prices = []
app_prices = bs.findAll("div", {"class": "search_price"})
for app_price in app_prices:
    # Remove the struck-out regular price of an app if it is on sale
    # Must be done before get_text() so each app has one price only
    for strike in app_price.select("strike"):
        strike.extract()
    app_price = app_price.get_text()
    # Remove price formatting
    app_price = re.sub(r"[CDN$]", '', app_price)
    # Remove unnecessary whitespace from price string
    app_price = re.sub(r"^\s+|\s+$", '', app_price)
    prices.append(app_price)

discount_percentages = [discount.get_text() for discount in bs.findAll(
        "div", {"class": "search_discount"})]
# Remove unnecessary whitespace from discount string
discount_percentages = [(re.sub(r"[^(?:\d+)]", '', discount))
                        for discount in discount_percentages]

# This section (review_summaries, num_reviews, positive_percentages) will
# need to be updated to handle recently released games with no reviews
review_summary_container = bs.findAll("span",
                                      {"class": "search_review_summary"})
review_summaries = [summary.get('data-tooltip-html')
                    for summary in review_summary_container]
# Extract review count
num_reviews = []
for review_count in review_summaries:
    review_count = re.findall(r"(?:\d+,\d+|\d+)[^\d+%]", review_count)[0]
    review_count = re.sub(r"^\s+|\s+$", '', review_count)
    num_reviews.append(review_count)
# Extract positive review percentages
positive_percentages = [(re.findall(r"(?:\d+)", summary)[0]) for summary in
                        review_summaries]

app_links = [link.get("href")
             for link in bs.find('div', {'id': 'search_resultsRows'})
                 .find_all('a', {'href': re.compile(r'(.com/app/\d+/)')})]

apps = pd.DataFrame({
    'title': app_titles,
    'release_date (yyyy-mm-dd)': dates,
    'price ($CDN)': prices,
    'discount (%)': discount_percentages,
    'review_count': num_reviews,
    'positive_reviews (%)': positive_percentages,
    'link': app_links
    })

# Data cleanup
# Price value errors ignored - 'Free' and 'Free to Play' are significant values
apps['release_date (yyyy-mm-dd)'] = pd.to_datetime(
        apps['release_date (''yyyy-mm-dd)'],
        format="%Y-%m-%d", errors='ignore')
apps['price ($CDN)'] = pd.to_numeric(apps['price ($CDN)'], errors='ignore')
apps['discount (%)'] = pd.to_numeric(apps['discount (%)'], errors='coerce') \
    .astype('Int64')
apps['review_count'] = apps['review_count'].str.replace(',', '').astype(int)
apps['positive_reviews (%)'] = apps['positive_reviews (%)'].astype(int)

apps.to_csv(f"{strftime('%Y-%m-%d %H-%M-%S')}_steam_oculus.csv")
