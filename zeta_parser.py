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

h = random_headers()['headers']
# r = requests.get(f'https://www.zkabel.ru/catalog/kabelnye-vvody-i-komplektujushhie/kabelnye-vvody-plastikovye/', headers=h,
#                  proxies=random_headers()['proxies'])
# латунь
r = requests.get(f'https://www.zkabel.ru/catalog/kabelnye-vvody-i-komplektujushhie/kabelnye-vvody/dlya-kruglogo-nebronirovannogo-kabelya-s-rezboy-m-g-pg-npt/', headers=h,
                 proxies=random_headers()['proxies'])


soup = BS(r.text, 'lxml')
#names = soup.find_all(string=re.compile('zeta\d\d\d\d\d'))
diams = soup.find_all(['th'],attrs={'scope': 'row', 'class':'b-table__cell'})
cabel = soup.find_all(string = re.compile('\d+-\d+([^/]|$)'), class_='b-table__cell')
price = soup.find_all(class_='price')

p= [x.get_text().strip() for x in price]
names = [x.get_text().strip() for x in diams if  not diams.index(x) % 2]
dms = [x.get_text().strip().replace('&nbsp','') for x in diams if  diams.index(x) % 2]
cables = [x.get_text().strip() for x in cabel]

rows =soup.find_all('tr',class_='item')
s= soup.tr.find_all(class_='b-table__cell')

print(cables)
print(p)
print(names)
print(dms)




for d in names:
        i = names.index(d)
        print(f'Кабель {cables[i]},Ввод пластиковый {dms[i]}; {names[i]}; {p[i]}')
        with open('some.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f,delimiter=';')
            writer.writerow(['Кабель ' + cables[i],'Ввод латунь '+ dms[i], names[i], p[i].replace('.',',')])


#print((set(diams)))
#print(rows)