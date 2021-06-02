import re

from bs4 import BeautifulSoup
import openpyxl
import pandas as pd
from urllib.request import urlopen

html = urlopen('https://www.amazon.ca/s?k=toaster&ref=nb_sb_noss').read()
bs = BeautifulSoup(html, 'html.parser')

product_names = [product.get_text()
                 for product in bs.findAll('span',
                                           {'class': "a-size-base-plus a-color-base a-text-normal"})]
# print(product_names)

ratings = [star.get_text() for star in bs.findAll('span',
                                                  {'class': 'a-icon-alt'})]
ratings = [(re.findall(r"\d\.\d", star)) for star in ratings]
# print(ratings)

prices = [price.get_text() for price in bs.findAll('span',
                                        {'class': "a-offscreen"})]
# print(prices)

links = [link.get("href")
         for link in bs.findAll('a', {'class': 'a-link-normal a-text-normal'})]
links = [('https://www.amazon.ca{}'.format(link)) for link in links]
# print(links)

output = []
for info in zip(product_names, ratings, prices, links):
    resp = {'product_name': info[0],
            'rating': info[1],
            'prices': info[2],
            'link': info[3]}
    output.append(resp)

df = pd.DataFrame(output)
df.to_excel('amazon_scrape.xlsx')
