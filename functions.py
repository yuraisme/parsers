import re
import logging
from typing import Any
from typing import Union
import random
from configparser import RawConfigParser
import cfscrape
import time
import readcsv
import requests
from pprint import pprint


class Config:
    def __init__(self, ini_file: str):
        self.ini_config = RawConfigParser()  # создаём объекта парсера
        if ini_file is not None:
            self.ini_config.read(ini_file)  # читаем конфиг
        else:
            logging.error(f'No ini file {ini_file}')

    def get_section(self, section: str, item: str = '') -> Union[dict, str]:
        """return section from ini as dictionary or str of item != "" """

        if section.lower() in self.ini_config.sections():
            if item != '':
                return dict(self.ini_config[section.lower()])[item.lower()]
            else:
                return dict(self.ini_config[section.lower()])

        else:
            logging.error(f'No {section} in .ini config')
            return {}


class Scrapping_sites:

    def __init__(self, ini_file: str):
        """
         Constor
        :param ini_file: str
        :return:
        """
        self.main_dict = {'Ticker': ''}
        self.main_dict['Name'] = ''
        self.main_dict['Description'] = ''
        self.main_dict['Description'] = ''
        self.main_dict['Category'] = ''
        self.main_dict['In_Category'] = ''
        self.main_dict['Country'] = ''
        self.names = list(self.main_dict.keys())

        self.config_file = ini_file
        self.scraper = cfscrape.create_scraper()

    def read_config(self):

        self.config = RawConfigParser()  # создаём объекта парсера
        self.config.read(self.config_file)  # читаем конфиг
        self.urls = dict(self.config['urls'])
        for urls in self.urls.keys():
            section = dict(self.config[urls])
            for attr in section.keys():
                if attr.title() not in self.names:
                    self.names += [attr.title()]
        return self.names

    def scrap_ticker(self, ticker: str, stock_list: None):
        """
        main function for scrapping ticker

        :param ticker:
        :return: -> dict(row for excel)
        """
        logging.info(f'Scrap for Ticker {ticker}')
        print(ticker)
        r = requests.Response()

        self.main_dict['Ticker'] = ticker
        if stock_list is not None:
            self.main_dict['Description'] = stock_list[ticker]

        for u, site in self.urls.items():
            logging.info(f'Scrapping Site: {u}, ticker: {ticker}')
            # headers = {'accept': '*/*', 'User-Agent': ua.random}
            headers = random_headers()['headers']
            proxy = random_headers()['proxies']

            section = dict(self.config[u])
            # r = self.scraper.get(site.replace('{ticker}', ticker), headers=headers, proxies=proxy)
            try:
                r = requests.get(site.replace('{ticker}', ticker), headers=headers, proxies=proxy)
                count = 1
                while r.status_code != 200 and count <= 3:
                    time.sleep(7)
                    logging.error(f'Have status {r.status_code} from "{u.upper()}" try again')
                    headers = random_headers()['headers']
                    proxy = random_headers()['proxies']
                    # r = self.scraper.get(site.replace('{ticker}', ticker), headers=headers, proxies=proxy)
                    r = requests.get(site.replace('{ticker}', ticker), headers=headers, proxies=proxy)

                    print(f'repeat request {count}')
                    print(r.status_code)
                    count += 1

            except Exception as e:
                logging.error(
                    f'Exception while get acces to {u.upper()}, response: {r.status_code}  proxy: {proxy}, {e}, ')

            finally:
                logging.info('Scraping page was is OK')

            for attr, path in section.items():
                mask = path
                atr = attr.title()

                try:
                    if re.search(mask, r.text) is not None:
                        print(atr, ':', re.search(mask, r.text).groups()[0])
                        self.main_dict[atr] = re.search(mask, r.text).groups()[0]
                    else:
                        print(atr, ':', 'None')
                        print(f'Warning!!! {ticker}, {u.upper()},')
                        logging.warning(f'Can\'t read "{attr.upper()}" from {u.upper()}. Request: {r.status_code}')
                        self.main_dict[atr] = '-'

                except Exception as e:
                    print(f'Exception!!!Ticker: {ticker}, Site: "{site.upper}", "{attr.upper()}" Message: {e}')
                    logging.error(f'Exception!!! {ticker}, "{site.upper()}", "{attr.upper()}", message {e}')
                    self.main_dict[attr.upper()] = '-'

        self.main_dict['Description'] = stock_list[ticker]
        logging.debug(f'All ROW: {self.main_dict}')
        return self.main_dict


def to_digit(s: str) -> Union[float, str, int]:
    """
    Convert STR digits to float of int

    :param s:str
    :return: float, integer,
    """
    out = s.strip()
    f_twin = r'\d+[,.]\d{2,} {0,}- {0,}\d+[.,]\d{2,}'
    f_rank = r'\d/10'
    f_score = r'[ ]{0,}\d+[ ]{0,}'
    f_date = r'\d\d\.\d\d\.\d\d\d\d'
    f_main = r'(-?\d*\,?\d+\.?\d*)[%BM]?'

    if isinstance(s, str) and re.findall(f_date, s) == [] and len(s) < 50 and s != '-':
        try:  # begin from big one, because bigs consist small re

            if re.search(f_main, s) is not None:
                res = re.search(f_main, s.strip()).groups()[0]
                if res == '-':
                    return '-'
                k = 1
                mul = 1
                after_point = res.split('.')
                if len(after_point) == 2:
                    k = 10 ** len(after_point[1].replace(',', ''))

                mul = 1000000000 if s.find('B') > 0 else mul     # found Billions
                mul = 1000000 if s.find('M') > 0 else mul        # found Millions
                mul = 0.01 if s.find('%') > 0 else mul           # found Percent format
                mul = mul * -1 if s.find(')') > 0 else mul       # financial format to show minus : -192.34 = (192.34)

                return round(float(res.replace('.', '').replace(',', '')), 2) * mul / k if k > 1 else \
                       int(res.replace('.', '').replace(',', '')) * mul

            if len(re.findall(f_twin, s)) > 0:  # format range xxx.xx - xxx.xx
                return float(re.findall(f_twin, s)[0]
                             .replace(' ', '')
                             .split('-')[0]
                             .replace(',', '')
                             .replace('.', '')) / 100

            if len(re.findall(f_rank, s)) > 0:  # format score like  9/10  -> 9
                return int(re.findall(f_rank, s)[0].split('/')[0])

            if len(re.findall(f_score, s)) > 0:  # format one digit score like ' 5 ' -> 5
                return int(re.findall(f_score, s)[0].replace(' ', ''))

        except Exception as e:

            logging.error(f"Error in to_digit(). Input {s}, Out ")
    return out


def random_headers() -> dict:
    """
    Generate random headers & proxy

    :return: dict {'headers': ->dict, 'proxies'->str}

    """
    ua = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2820.59 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; de) Opera 11.01',
        'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
        'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.9.168 Version/11.51',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)',
        'Opera/9.80 (Windows NT 6.1; U; en-GB) Presto/2.7.62 Version/11.00',
        'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.9.168 Version/11.51',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36&quot;',

    ]
    proxies = [  # from  proxyline.net
        {"http": "http://lt21YkhCyb:EavRl1DnlB@45.146.26.12:53341"},
        {"http": "http://lt21YkhCyb:EavRl1DnlB@146.71.87.153:54631"},
        {"http": "http://lt21YkhCyb:EavRl1DnlB@144.208.126.128:45871"},
        {},
    ]
    headers = {'User-Agent': random.choice(ua),
               'accept': '*/*',
               }
    proxies = random.choice(proxies)
    return {'headers': headers, 'proxies': proxies}


if __name__ == "__main__":

    print(to_digit(r'28.10.2010'))  # code for check functions
    print(to_digit(r'\n\n   9/10\n\n'))
    print(to_digit(r'-98.2B'))
    print(to_digit(r'1,456.98%'))
    print(to_digit(r'(10.68B)'))
    print(to_digit(r'12.7%'))
    print(to_digit(r'12.77%'))
    print(to_digit(r'(76M)'))
    print(to_digit(r'76M'))
    print(to_digit(r'12.09B'))
    print(to_digit(r'-10.1%'))
    print(to_digit(r'0.01%'))
    print(to_digit(r'23,456.34'))
    print(to_digit(r'23,456.34B'))
    print(to_digit(r'834.55 - 457.45'))
    print(to_digit(r'   8   '))

    print(random_headers()['headers'])

    FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
    logging.basicConfig(format='%(asctime)s[ %(levelname)s ] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
                        datefmt='%d.%m.%y %H:%M:%S: ',
                        filename='temp_log.log', level=logging.INFO, filemode='a')

    scraper = Scrapping_sites('config.ini')
    print(scraper.read_config())
    ps = readcsv.piter_stocks('stocks_list.xlsx')
    for ticker in ps.tickers:
        print('==============')
        scraper.scrap_ticker(ticker, ps.descriptions)
        pprint(scraper.main_dict)
        time.sleep(6)
