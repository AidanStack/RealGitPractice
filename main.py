################## 1: Import All Relevant Modules and libraries  #################
import pandas_datareader.data as web
import pandas as pd
from tabulate import tabulate
import matplotlib
import seaborn
import datetime
from datetime import date
from IPython.display import display
from matplotlib import pyplot as plt
import smtplib

from bs4 import BeautifulSoup
import requests


#print(date.today())


#
################ 2: Scrape yahoo for S&P 500 (SPY) historical price data #################




# start = datetime.datetime(1993, 1 , 29)
# end = datetime.datetime(2021, 2, 8)
# #  hsd stands for historical SPY data
# SPY = web.DataReader('SPY', 'yahoo', start, end)
# pd.set_option('display.max_rows', None,'display.max_columns', None,)
# print(SPY.tail())
# years = [x for x in range(1993, 2022)]
# plt.plot(range(len(SPY.Close)), SPY['Close'])
# plt.xlabel('Year')
# plt.ylabel('Price')
# plt.show()
# # print(SPY.tail())
# # display(SPY)
# #
# # plt.plot(range(len(SPY.High)), SPY['Close'])
# #
# #
# # plt.show()
# #


#
################## 3: Create a dictionary that holds the item name, and actionfigure411 url  ##################


url_dict = {'R2D2':'https://www.actionfigure411.com/star-wars/6-black-series/orange-wave-2013/r2d2-4.php',

            'Clone Commander Fox':'https://www.actionfigure411.com/star-wars/6-black-series/exclusives/clone-commander-'
                                  'fox-1319.php',

            'Clone Captain Rex':'https://www.actionfigure411.com/star-wars/6-black-series/force-awakens-2015-2018/clone-'
                                'captain-rex-934.php',

            'Incinerator Trooper':'https://www.actionfigure411.com/star-wars/6-black-series/galaxy/incinerator-trooper-'
                                  '1537.php',

            #'Admiral Ackbar':'https://www.actionfigure411.com/star-wars/6-black-series/galaxy/admiral-ackbar-1409.php',

            'Q9-0':'https://www.actionfigure411.com/star-wars/6-black-series/galaxy/q9-0-zero-2079.php',

            'Mandalorian (Beskar Armor)':'https://www.actionfigure411.com/star-wars/6-black-series/galaxy/mandalorian'
                                         '-beskar-armor-1412.php',

            'Clone Commander Obi-Wan':'https://www.actionfigure411.com/star-wars/6-black-series/exclusives/clone-commander-obi-wan-kenobi-1247.php',

            'Supreme Leader Kylo Ren':'https://www.actionfigure411.com/star-wars/6-black-series/force-awakens-2015-2018/supreme-leader-kylo-ren-1287.php'
                    }
catalog = {}

portfolio = {}

sold_items = {}

def web_scraper(url):
    # Some websites try to prevent web scraping, these headers will help us try to get around that if necessary.

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

    req = requests.get(url, headers).text
    soup = BeautifulSoup(req, 'lxml')
    #print(soup.prettify())
    return soup

def add_item_to_catalog(item_name, url):
    html_version = web_scraper(url)
    catalog[item_name] = {'Item Name':item_name}

    # This for loop makes a string of the title block of the html file. This title includes the current avg market price
    # for the item, so it finds the number after the $ in the title, converts it to an int, an adds it to the catalog.
    current_price = ''
    for i in range(len(str(html_version.title))):
        nums = '1234567890.'
        if str(html_version.title)[i] == '$':
            for j in range(i,len(str(html_version.title))):
                if str(html_version.title)[j] in nums:
                    current_price += str(html_version.title)[j]
            break
    catalog[item_name]['Current Price'] = round(
        int(current_price.split('.')[0]) + int(current_price.split('.')[1]) ** .01, 2)

    # This for loop creates a list of all the <b> tags in the html file, and iterates through string versions of that
    # list until it finds a string that contains the word year. Once it finds that tag, using the .next_sibling method,
    # it adds the text that follows the <b> tag to the items catalog entry under the key 'Year'.
    item_year = None
    for i in range(len(html_version.find_all('b'))):
        if str(html_version.find_all('b')[i]).count('Year') == 1:
            item_year = html_version.find_all('b')[i].next_sibling
            break
    catalog[item_name]['year'] = int(item_year.replace(':','').strip())

    # This for loop works in the exact same way as the loop above, but it obtains the retail price.
    retail = ''
    for i in range(len(html_version.find_all('b'))):
        if str(html_version.find_all('b')[i]).count('Retail') == 1:
            retail = html_version.find_all('b')[i].next_sibling
            break
    catalog[item_name]['Retail'] = retail.replace(' ','').replace(':','')
    # Here Item Number is used to keep track of how many of each figure has been purchased (dont think this is required)
    #catalog[item_name]['Item Number'] = 1


def item_bought(item_name, purchase_price, purchase_date):
    item_number = 0
    for i in range(1000):
        if i not in [x for x in portfolio.keys()] and i not in [x for x in sold_items.keys()] and i != 0:
            item_number = i
            break
    portfolio[item_number] = catalog[item_name]
    portfolio[item_number]['Purchase Price'] = purchase_price
    portfolio[item_number]['Purchase Date'] = purchase_date
    # The following line of code calculates our first statistic, 'ebay alpha'. This metric takes the current market
    # value and subtracts 13% for ebay's fee, ebay's $0.30 transaction fee, and the cost to purchase the item. This
    # metric gives a theoretical current net value of each item based on how much it cost, and the avg market price.
    # This calculation also assumes a shipping cost of $10.
    portfolio[item_number]['ebay alpha'] = round((catalog[item_name]['Current Price']) - (catalog[item_name]['Current '
                                            'Price'] + 10) * .13  - portfolio[item_number]['Purchase Price'] - .30, 2)
    # The code below calculates the 'ebay break even price' metric. This is the number that takes the given the
    # purchase price of an item, and the ebay selling costs formula and finds what price it would need to sell at to
    # break even.
    # The formula I wrote for 'ebay break even price' (x) is this -
    # x - (x + 10) * .13 -.30 = Purchase Price
    # An online formula simplifier converted the formula to this, where PP is the purchase price for a given item.
    #    3 * (712151 * PP + 1139500) / 1858703
    portfolio[item_number]['ebay break even price'] = round((3 * ((712151*portfolio[item_number]['Purchase '
                                                                                'Price'] ) + 1139500)) / 1858703,2)
    # Market Delta tracks the difference between the current market price, and the current break even price.
    # If negative this is the amount the price of the item 'still needs to go' and if positive is the amount the items
    # price 'has gone'
    portfolio[item_number]['Market Delta'] = round( portfolio[item_number]['ebay break even price'] - portfolio
                                                                                [item_number]['Current Price'],2)

def item_sold(item_number, date_sold, sale_price):
    sold_items[item_number] = (portfolio[item_number])
    portfolio.pop(item_number)
    sold_items[item_number]['Sale Date'] = date_sold
    sold_items[item_number]['Sale Price'] = sale_price

# # Individual Portfolio Item Statistics
#     real dollar change in current price since purchase
#     % change in price since purchase
#     % change in price vs SPY
#     rank all currently held figures by DOLLAR change in profit   (include % change, but dont rank by this metric)
#
#          The table should follow the format below, and be ranked in descending order of dollar change
#     Item Number -       Name       -    Purchase Price   -   Current Price  -  Dollar Change - % Change  -
#
#
#
# # Portfolio Statistics
#
#
#
#   total dollar change
#
# # Individual Sold Item Statistics
            # this will be the format of the output table for all sold items
#     Item Number -       Name       -    Purchase Price   -   Sale Price  -  Gains or Losses -  % Change
#
# # Sold Items Statistics
#
#    total historic realized gains/losses
#% change of all items together vs % change SPY in same timeframe
#      # for the above statistic, I will have to calculate the SPY returns for the amount each figure was bought for, for the
#      # period it was owned for, and sum/avg these together
#
# State the unrealized total Loss / Gain
# State the total realized Loss / Gain
#
# State the sum of these two

#


def stats_calculator(item_number):
    if item_number in [x for x in sold_items.keys()]:
        starting_date = sold_items[item_number]['Purchase Date']
        end_date = sold_items[item_number]['Sale Date']
        starting_price = sold_items[item_number]['Purchase Price']
        sale_price = sold_items[item_number]['Sale Price']
    else:
        starting_date = portfolio[item_number]['Purchase Date']
        end_date = portfolio[item_number]['Sale Date']
        starting_price = portfolio[item_number]['Purchase Price']
        sale_price = portfolio[item_number]['Sale Price']





def run_portfolio_analysis(portfolio):
    pass







# This list will have to be manually edited everytime a figure is purchased.
# Make sure that the item_name is identical to the catalog entry for that figure.

purchased_items = [ ['Mandalorian (Beskar Armor)',30.50,'2020-11-15'],
                    #['Admiral Ackbar', 17.41 , '2021-6-6'],
                    ['Q9-0', 30.04, '2021-6-6'],
                    ['Incinerator Trooper', 30.15, '2021-6-6'],
                    ['R2D2', 78.39, '2021-6-6'],
                    ['Clone Captain Rex', 86.28 , '2021-6-6'],
                    ['Clone Commander Fox', 101.80, '2021-6-8'],
                    ['Clone Commander Obi-Wan', 91.46, '2021-6-10'],
                    ['Supreme Leader Kylo Ren',18.24,'2021-6-10']
                    ]

# These completed items are items that have been sold, the dict sold_items holds the final data on these.
completed_items = [ [5, '2021-6-11', 90] , [3, '2021-6-11', 120 ] ]

for i in url_dict.keys():
    print(i)
    add_item_to_catalog(i,url_dict[i])

print('    CATALOG')
for i in catalog:
    print(i , catalog[i] )

print( '''
''')
# Should I make custom functions for these four actions? So i can just call them down here?

for i in purchased_items:
    item_bought(i[0],i[1],i[2])

#for i in completed_items:
 #   item_sold(i[0],i[1],i[2])

print('     PORTFOLIO')
for i in portfolio:
    print ( i , portfolio[i])
    print(' ')

print('''
''')

# print('     SOLD ITEMS')
# for i in sold_items:
#     print(i, sold_items[i])

current_portfolio_value = 0












#print(web_scraper('https://www.actionfigure411.com/star-wars/6-black-series/exclusives/c-3po-anh-195.php'))

#     * Create a function that auto generates classes from scraped web data?
#     * each individual item will be an instance of its models class
#         will include relevant data for each item
#             mainly purchas price
#         will build a price history for this item over time
#
################## 4: Calculate Stats for each figure   #################
#     * absolute value change
#     * percent change
#
################## 5: Calculate stats for entire collection:   #################
#     * absolute value change
#     * total percent change vs SPY total percent change
#
# 6: Generate report containing all of this information
#
#     * Table with each individual items
#         purchased for
#         current value
#         absolute change
#         percent change
#
#     graph of the S&P 500 vs figure collection value
#
################## 7: Automatically email that report to aidanstack6@gmail.com   #####################

bot_email = 'stackbot6@gmail.com'
password = 'MrCodfish3!'
destination_email = 'aidanstack6@gmail.com'


def send_email(recipient, message):

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login('stackbot6@gmail.com', 'jmkaphzwlcpxfvzp')


        message = 'empty test report'

        smtp.sendmail(bot_email, recipient, message)

        smtp.quit()

# report = ' '

# send_email(destination_email, report)


pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.width',1000 , )
#pd.set_option('display.height', 500)

#R2D2 = pd.read_html('https://www.actionfigure411.com/star-wars/6-black-series/orange-wave-2013/r2d2-4.php')
#
# for i in range(len(R2D2)):
#     print("""
#
#
#
#
#     """)
#     print(tabulate(R2D2[i]))