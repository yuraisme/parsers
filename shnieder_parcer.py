from pprint import pprint
import readcsv
from parsel import Selector
from requests_html import HTMLSession
import requests
import re
import urllib
# import pymysql
from datetime import date
import datetime
import pandas as pd
import re
import configparser as cp
import time
from fake_useragent import UserAgent
import readcsv
import csv
import cfscrape
from functions import random_headers
import dbaccess
from pprint import pprint
from collections import namedtuple
from collections import  deque
from jinja2 import Template
from bs4 import BeautifulSoup as BS

with open('schnieder.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')

for page in range(1, 13):
    h = random_headers()['headers']
    r = requests.get(f'https://e-kc.ru/price/avtomaticheskij-vyklyuchatel-differentsialnogo-toka-difavtomat-avdt/schneider_electric?page={page}', headers=h)


    soup = BS(r.text, 'lxml')
    names = soup.find_all('a',attrs={'data-product':re.compile('\d+')})
    prices = soup.find_all('span', 'price')
    print(prices)

    for i in names:
        try:
            with open('schnieder.csv', 'a', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                row = []
                if 'Schneider Electric' in  i.get_text():
                    row.append(i.get_text()) #name

                    if i.get('href').split('-')[-1].upper() =='SCHNIEDER':
                        row.append(i.get('href').split('-')[-3].upper()) #order number
                    else:
                        row.append(i.get('href').split('-')[-1].upper())  # order number

                    row.append(prices[names.index(i)].get_text().replace(' ','').replace('.',','))
                    writer.writerow(row)
                    print(row)

        except Exception as e:
            print(f'Exception! {e}')
    print(f'Page count is #{page}')
    time.sleep(10)





#print((set(diams)))
#print(rows)