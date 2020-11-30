import requests
from bs4 import BeautifulSoup as BS
from functions import random_headers
from pprint import pprint
from functions import  to_digit
import dbaccess
import readcsv as ps
import time
import spreadsheets

db = dbaccess.DBConnect()
stocks = ps.piter_stocks('stocks_list.xlsx')
head = ['Ticker',	'Net_Income_Growth',	'Depreciation_Depletion_and_Amortization',	'Depreciation_and_Depletion',	'Amortization_of_Intangible_Assets',	'Deferred_Taxes_and_Investment_Tax_Credit',	'Deferred_Taxes',	'Investment_Tax_Credit',	'Other_Funds',	'Funds_from_Operations',	'Extraordinaries',	'Changes_in_Working_Capital',	'Receivables',	'Accounts_Payable',	'Other_Assets_to_Liabilities',	'Net_Operating_Cash_Flow',	'Net_Operating_Cash_Flow_Growth',	'Net_Operating_Cash_Flow_to_Sales',	'Capital_Expenditures',	'Capital_Expenditures_Fixed_Assets',	'Capital_Expenditures_Other_Assets',	'Capital_Expenditures_Growth',	'Capital_Expenditures_to_Sales',	'Net_Assets_from_Acquisitions',	'Sale_of_Fixed_Assets_and_Businesses',	'Purchase_to_Sale_of_Investments',	'Purchase_of_Investments',	'Sale_to_Maturity_of_Investments',	'Other_Uses',	'Other_Sources',	'Net_Investing_Cash_Flow',	'Net_Investing_Cash_Flow_Growth',	'Net_Investing_Cash_Flow_to_Sales',	'Cash_Dividends_Paid__Total',	'Common_Dividends',	'Preferred_Dividends',	'Change_in_Capital_Stock',	'Repurchase_of_Common_and_Preferred_Stk',	'Sale_of_Common_and_Preferred_Stock',	'Proceeds_from_Stock_Options',	'Other_Proceeds_from_Sale_of_Stock',	'Issuance_to_Reduction_of_Debt_Net',	'Change_in_Current_Debt',	'Change_in_LongTerm_Debt',	'Issuance_of_LongTerm_Debt',	'Reduction_in_LongTerm_Debt',	'F_Other_Funds',	'F_Other_Uses',	'F_Other_Sources',	'Net_Financing_Cash_Flow',	'Net_Financing_Cash_Flow_Growth',	'Net_Financing_Cash_Flow_to_Sales',	'Exchange_Rate_Effect',	'Miscellaneous_Funds',	'Net_Change_in_Cash',	'Free_Cash_Flow',	'Free_Cash_Flow_Growth',	'Free_Cash_Flow_Yield',	'Net_Income_before_Extraordinaries',	'Cash_Dividends_Paid_Total',	'Funds_from_Operations_Growth',	'Cash_Dividend_Growth',	'Inventories',	'Net_Operating_Cash_Flow_to_Interest_Income',	'Increase_in_Loans',	'Decrease_in_Loans',	'Net_Investing_Cash_Flow_to_Interest_Income',	'Decrease_in_Deposits',	'Increase_in_Deposits',	'Net_Financing_Cash_Flow_to_Interest_Income'
]

google_sheet = spreadsheets.Google_sheets('2015')
google_sheet.SPREADSHEET_ID = '1Xoemx1wIWmgpzlr7YZllvH-DEEAWi1MdlHy4b7veZ_Y'
google_sheet.connect()
for i in ['2016','2017','2018','2019','2020']:
    google_sheet.select_sheet(i)
    google_sheet.set_size(80, 1500)

    # google_sheet.write_head(head)
exit(10)

stat_2016 = []
stat_2017 = []
stat_2018 = []
stat_2019 = []
stat_2020 = []
names = []
name = ''

r = requests.get('https://www.ya.ru')
#stocks.tickers = ['ABG','ABC','AJG']
for ticker in stocks.tickers:


    print(ticker)
    for trying in range(3):
        h = random_headers()['headers']
        r = requests.get(f'https://www.marketwatch.com/investing/stock/{ticker}/financials/cash-flow', headers=h, proxies=random_headers()['proxies'])
        if r.status_code == 200:
            break
        time.sleep(10)
        print(f'Trying {trying} times!!\n')

    if r.text is not None and r.status_code == 200:
        soup = BS(r.text, 'lxml')
        res = soup.find_all(attrs={"class": "rowTitle"})
        values = soup.find_all(attrs={"class": "valueCell"})  #можно так
        years = soup.find_all(scope_='col')  # а можно вот так
        stat_years = []
        pprint(years)


        if res != [] and values != [] and years != []:

            del res[0]
            j = 0
            cnt = 0
            for y in years: # получем годы за которую дадут статистику
                stat_years.append(y.get_text())
                cnt += 1
                if cnt == 5:
                    break
            pprint(stat_years[0])

            cnt = 0
            for i in res:
                if i.get_text() != '':
                    name = i.get_text().strip().replace('/','_to_')\
                                                .replace(' ','_')\
                                                .replace('&','and')\
                                                .replace('(','')\
                                                .replace(')','')\
                                                .replace('.', '')\
                                                .replace(',', '')\
                                                .replace('-', '')\
                                                .replace('__', '_')
                    if cnt == 2:
                        if name =='Other_Funds':
                             names.append('F_Other_Funds')
                        elif name =='Other_Uses':
                            names.append('F_Other_Uses')
                        elif name == 'Other_Sources':
                            names.append('F_Other_Sources')

                        else:
                            names.append(name)
                    else:
                        names.append(name)

                    print(name, ":",   values[j].get_text(),'|',
                                       values[j+1].get_text(),'|',
                                       values[j+2].get_text(),'|',
                                       values[j+3].get_text(),'|',
                                       values[j+4].get_text(),'|'
                          )
                    stat_2016.append(to_digit(values[j].get_text()))
                    stat_2017.append(to_digit(values[j+1].get_text()))
                    stat_2018.append(to_digit(values[j+2].get_text()))
                    stat_2019.append(to_digit(values[j+3].get_text()))
                    stat_2020.append(to_digit(values[j+4].get_text()))
                    j += 5
                else:
                    cnt += 1
                    print(end='\n\n')
                    if cnt == 1:
                        print('==========Investing Activities==========')
                    elif cnt == 2:
                        print('===========Financing Activities=========')


            s_2016 = dict(zip(names,stat_2016))
            s_2016['Ticker'] = ticker

            s_2017 = dict(zip(names,stat_2017))
            s_2017['Ticker'] = ticker

            s_2018 = dict(zip(names,stat_2018))
            s_2018['Ticker'] = ticker

            s_2019 = dict(zip(names,stat_2019))
            s_2019['Ticker'] = ticker

            s_2020 = dict(zip(names,stat_2020))
            s_2020['Ticker'] = ticker
            db.add_sqlite(f'financials_{stat_years[0]}', s_2016)
            db.add_sqlite(f'financials_{stat_years[1]}', s_2017)
            db.add_sqlite(f'financials_{stat_years[2]}', s_2018)
            db.add_sqlite(f'financials_{stat_years[3]}', s_2019)
            db.add_sqlite(f'financials_{stat_years[4]}', s_2020)
            pprint(s_2019)

            stat_2016.clear()
            stat_2017.clear()
            stat_2018.clear()
            stat_2019.clear()
            stat_2020.clear()

            s_2016.clear()
            s_2017.clear()
            s_2018.clear()
            s_2019.clear()
            s_2020.clear()
            names.clear()
            print()
            print(f'^^^^^^ was ticker {ticker} ^^^^^')
            time.sleep(10)




