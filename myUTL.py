
import sys
from datetime import date
import requests  # https://requests.readthedocs.io/en/master/
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

from urlLib import *
from ticker import snp500

# constants
MILLION = 1000000
BILLION = 1000000000

# For debug
import inspect


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


DEBUG = 0
def DBG(msg):
    if DEBUG:
        print(msg)


def ERROR(msg):
    print(msg)
    sys.exit()


def WARNING(msg):
    print(msg)


PRINT_ENABLED = 1
def _print(msg):
    if PRINT_ENABLED:
        print(msg)


# Global variables

# The Session object allows you to persist certain parameters across requests.
# It also persists cookies across all requests made from the Session instance.
session = requests.Session()


def remove_empty_lines(text):
    new_text = ""
    new_line_added = 0
    for data in text.split('\n'):
        if data and data != '\n':
            new_text += data
            new_line_added = 0
        elif not data and new_line_added == 0:
            new_text += '\n'
            new_line_added = 1
    return new_text


def remove_alpha(text):
    new_text = ""
    for char in text:
        if not char.isalpha():
            new_text += char
    return new_text


def remove_whitespace(text):
    new_text = ""
    for char in text:
        if not char.isspace() or char == '\n':   # isspace() also remove newline char but we want that in
            new_text += char
    return new_text


def extract_table(tables, table_name):
    multiples = 1
    table_dict = {}
    for i in range(0, tables.__len__()):
        table = tables[i]
        if str(table).__contains__(table_name):
            # Found the table.
            # Check if values are in millions or billions
            if str(table).__contains__("Millions"):
                multiples = MILLION
            elif str(table).__contains__("Billions"):
                multiples = BILLION
            else:
                multiples = 1
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                # print(row)
                if len(row) == 2:
                    # table could be annual or quarterly
                    # Quarterly: row[0] is date and row[1] is value
                    # Annual:    row[0] is year and row[1] is value
                    value = str(row[1]).replace(',', '')
                    value = value.replace('$', '')
                    if value == '':  # Sometimes the value could be empty
                        value = 0
                    if str(row[0]).__contains__('-'):
                        # this is Quarterly table
                        d = row[0].split('-')
                        my_date = date(int(d[0]), int(d[1]), int(d[2]))  # year/month/day
                        table_dict[my_date] = float(value) * multiples
                    else:
                        # this is annual table
                        table_dict[int(row[0])] = float(value) * multiples
            return table_dict

    # If we exit for loop then that means we did not find the table in the list is tables.
    ERROR("Table not found")
    return 'NAN'


def extract_eps_history(url):
    soup = get_html(url)
    body = soup.find("body")
    tables = body.find_all("table")
    annual_eps_table = tables[0]
    quarterly_eps_table = tables[1]

    annual_eps_dict = {}
    quarterly_eps_dict = {}

    table_rows = annual_eps_table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        # print(row)
        if len(row) == 2:
            annual_eps_dict[int(row[0])] = float(row[1].split('$')[1])

    table_rows = quarterly_eps_table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        # print(row)
        if len(row) == 2:
            # row[0] is date and row[1] is earning
            d = row[0].split('-')
            my_date = date(int(d[0]), int(d[1]), int(d[2]))  # year/month/day
            quarterly_eps_dict[my_date] = float(row[1].split('$')[1])

    _print("Annual EPS: ")
    _print(annual_eps_dict)
    _print("Quarterly EPS: ")
    _print(quarterly_eps_dict)
    return {"annual": annual_eps_dict, "quarterly": quarterly_eps_dict}


def get_divided_yield_history(ticker):
    url = get_dividend_url_nasdaq(ticker, snp500[ticker])
    soup = get_html(url)
    title = soup.find("title")
    if not title.text.__contains__('Dividend Yield'):
        url = get_dividend_url_nyse(ticker, snp500[ticker])
        soup = get_html(url)
        title = soup.find("title")
        if not title.text.__contains__('Dividend Yield'):
            # This mostly will happen if the company does not have any dividend record so far
            WARNING("Unable to open dividend yield page. line number: " + str(lineno()))
            return {"dividend_amt": {}, "dividend_yield": {}}

    dividend_amt_dict = {}
    dividend_yield_dict = {}

    body = soup.find("body")
    tables = body.find_all("table")
    # NOTE: the table format is different for the webpage that gives dividend info. So using a different logic here.
    # Also cannot verify the table title because that is not part of the table
    if tables.__len__() < 2:
        return {"dividend_amt": {}, "dividend_yield": {}}

    table = tables[1]  # this second table has dividend history

    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        # print(row)
        if len(row) == 7:
            dt = row[0].split('/')
            _div = row[2].split('$')
            _yield = row[3].split('%')
            mydate = date(int(dt[2]), int(dt[0]), int(dt[1]))
            dividend_amt_dict[mydate] = float(_div[1])
            dividend_yield_dict[mydate] = float(_yield[0]) if _yield[0] else 0.0
    _print("Dividend amount ($):")
    _print(dividend_amt_dict)
    _print("Dividend yield (%):")
    _print(dividend_yield_dict)
    return {"dividend_amt": dividend_amt_dict, "dividend_yield": dividend_yield_dict}


# This API is invalid current. We can find text "Dividend YieldN/A" on webpage
# Even if dividend info is provided in the table. Hence misleading results.
def dividend_yield_available(ticker):
    url = get_dividend_url_nasdaq(ticker, snp500[ticker])
    soup = get_html(url)
    title = soup.find("title")
    if not title.text.__contains__('Dividend Yield'):
        url = get_dividend_url_nyse(ticker, snp500[ticker])
        # At this stage we don't need to check if the page title contains "Dividend Yield", because...
        # If we are unable to open dividend yield page, then it is possible that the dividend yield is not available
        # for this company.
        # In that case,  just search for the string below.

    if http_get_text(url).__contains__("Dividend YieldN/A"):
        return 0
    else:
        return 1


# Returns all text in body of the webpage
def http_get_text(url):
    global session
    # open with GET method
    DBG("http_get_text() requests.get(url)")
    resp = session.get(url)

    # http_response 200 means OK status
    if resp.status_code == 200:
        # Create a soup object
        soup = BeautifulSoup(resp.content, features="html.parser")
        body = soup.find("body")
        return str(body.text)
    elif resp.status_code == 401:
        resp = session.get(url, auth=HTTPBasicAuth('user', 'pass'))
        if resp.status_code == 200:
            # Create a soup object
            soup = BeautifulSoup(resp.content, features="html.parser")
            body = soup.find("body")
            return str(body.text)
        else:
            ERROR("Error. resp:" + str(resp.status_code))
    else:
        ERROR("Error. resp:" + str(resp.status_code))
    sys.exit()


def get_html(url):
    global session
    # open with GET method
    DBG("get_html() requests.get(url)")
    resp = session.get(url)
    # http_response 200 means OK status
    if resp.status_code == 200:
        # Create a soup object
        soup = BeautifulSoup(resp.content, features="html.parser")
        return soup
    elif resp.status_code == 401:
        resp = session.get(url, auth=HTTPBasicAuth('user', 'pass'))
        if resp.status_code == 200:
            # Create a soup object
            soup = BeautifulSoup(resp.content, features="html.parser")
            return soup
        else:
            ERROR("Error. resp:" + str(resp.status_code))
    else:
        ERROR("Error. resp:" + str(resp.status_code))
    sys.exit()


# Returns: {"annual": annual_eps_dict, "quarterly": quarterly_eps_dict}
def get_eps_history(ticker):
    url = get_eps_url(ticker, snp500[ticker])
    return extract_eps_history(url)


def get_stock_price(ticker):
    url = get_price_url(ticker, snp500[ticker])
    text = http_get_text(url)
    lines = text.split('\n')
    for line in lines:
        if len(line) and line.__contains__("The latest closing stock price"):
            # Expected line here is:
            # Historical daily share price chart and data for Apple since 1980 adjusted for splits.  The latest closing stock price for Apple as of November 20, 2020 is 117.34.
            words = line.split(' is ')
            price = float(words[1].split('. ')[0])
            return price
    return 0


def get_shares_outstanding(ticker):
    url = get_shares_outstanding_url(ticker, snp500[ticker])
    soup = get_html(url)
    title = soup.find("title")
    if title.text.__contains__('Shares Outstanding'):
        body = soup.find("body")
        tables = body.find_all("table")
        quarterly_shares_outstanding_dict = extract_table(tables, 'Quarterly Shares Outstanding')
        if quarterly_shares_outstanding_dict == 'NAN':
            WARNING("Unable to extract shares" + str(lineno()))
            return 'NAN'
        latest_date = list(quarterly_shares_outstanding_dict.keys())[0]
        return quarterly_shares_outstanding_dict[latest_date]


# Book value or net assets = Total assets - total liabilities
# Book value per share = book value / total number of shares
# P/B ratio = Share price / Book value per share
def get_pb_ratio(ticker, financial_data, stock_price):
    total_assets = financial_data["total_assets"]
    liabilities = financial_data["liabilities"]
    # lon_term_debt = get_long_term_debt(ticker)
    book_value = float(total_assets - liabilities)
    shares = get_shares_outstanding(ticker)
    if 0.0 >= float(shares):
        ERROR("Number of shares cannot be less than 0")
    bvps = float(book_value / shares)
    pb_ratio = stock_price/bvps
    return pb_ratio


def get_pe_ratio(ticker, eps_history, num_yrs_avg, price ):
    eps_annual_dict = eps_history["annual"]
    num_years = num_yrs_avg
    total_eps = 0
    pe_ratio = 0
    for key in eps_annual_dict:
        year = key
        total_eps += eps_annual_dict[year]
        num_years -= 1
        if num_years == 0:
            break
    if num_years == 0:
        avg_eps = total_eps / num_yrs_avg
        pe_ratio = float(price / avg_eps)
    else:
        # looks like company does not have earnings for all the last "num_yrs_avg" years
        # In this case, lets calculate PE ratio according to the available earnings
        avg_eps = total_eps / (num_yrs_avg - num_years)
        pe_ratio = float(price / avg_eps)
        _print("company does not have earnings for all " + str(num_yrs_avg) + ' years. Only ' + str(num_years) + " years.")

    _print("P/E ratio: " + str(pe_ratio))
    return pe_ratio


# Returns company stock price according to 25 times earning
def get_max_pe_fair_price(ticker, eps_history, num_yrs_avg, pe_ratio):
    eps_annual_dict = eps_history["annual"]
    num_years = num_yrs_avg
    total_eps = 0

    for key in eps_annual_dict:
        year = key
        total_eps += eps_annual_dict[year]
        num_years -= 1
        if num_years == 0:
            break
    if num_years == 0:
        avg_eps = total_eps / num_yrs_avg
    else:
        # looks like company does not have earnings for all the last "num_yrs_avg" years
        # In this case, lets calculate PE ratio according to the available earnings
        avg_eps = total_eps / (num_yrs_avg - num_years)
        _print("company does not have earnings for all " + str(num_yrs_avg) + ' years. Only ' + str(num_years) + " years.")

    max_fair_price = float(pe_ratio * avg_eps)
    _print("max_fair_price for" + str(pe_ratio) + " PE ratio: " + str(max_fair_price))
    return max_fair_price


# https://www.macrotrends.net for market cap has a bug where it can only
# show market caps of up to 1000B. But that is OK for me.
def get_market_cap(ticker):
    url = get_market_cap_url(ticker, snp500[ticker])
    text = http_get_text(url)
    lines = text.split('\n')
    for line in lines:
        if len(line) and line.__contains__(
                "Market capitalization (or market value) is the most commonly used method of measuring the size"):
            # Expected line here is:
            # Apple market cap history and chart from 2006 to 2020. Market capitalization (or market value) is the most
            # commonly used method of measuring the size of a publicly traded company and is calculated by multiplying
            # the current stock price by the number of shares outstanding. Apple market cap as of November 20, 2020 is
            # $1000B.
            words = line.split(' is $')
            price = 0
            if words[1].__contains__('B'):
                price = words[1].split('B')[0]
            else:
                ERROR("ERROR: Value is not in Billions. " + "    line: " + str(lineno()))
            price = price.replace(',', '')
            price = float(price)
            return price
    return 0


def get_total_curr_asset_value(ticker):
    url = get_total_asset_url(ticker, snp500[ticker])
    soup = get_html(url)
    body = soup.find("body")
    tables = body.find_all("table")

    # We only store assets every quarter. Since assets latest quarter is the total assets anyways
    # and does not add/subtract (or has anything to do) with the assets in past quarter.
    total_quarterly_asset_dict = extract_table(tables, 'Quarterly Total Assets')
    if total_quarterly_asset_dict == 'NAN':
        WARNING("Unable to get current asset")
        return 'NAN'
    latest_date = list(total_quarterly_asset_dict.keys())[0]
    return total_quarterly_asset_dict[latest_date]


def get_total_curr_liabilities(ticker):
    url = get_liabilities_url(ticker, snp500[ticker])
    soup = get_html(url)
    body = soup.find("body")
    tables = body.find_all("table")

    # We only store liabilities every quarter. Since liabilities latest quarter is the total anyways
    # and does not add/subtract (or has anything to do) with the liabilities in past quarter.
    total_quarterly_liabilities_dict = extract_table(tables, 'Quarterly Total Liabilities')
    if total_quarterly_liabilities_dict == 'NAN':
        WARNING("Unable to get current asset")
        return 'NAN'

    latest_date = list(total_quarterly_liabilities_dict.keys())[0]
    return total_quarterly_liabilities_dict[latest_date]


def get_cumulative_earning_growth(eps_history, num_yrs):
    latest_date = 0
    quarterly_earning_dict = eps_history["quarterly"]
    annual_earning_dict = eps_history["annual"]
    curr_yr_earning = 0
    quarters = 0

    # Get the latest date
    for key in quarterly_earning_dict:
        latest_date = key
        break

    # take current year's earning is in quarterly list.
    for key in quarterly_earning_dict:
        quarter_date = key
        if quarter_date.year < latest_date.year:
            break
        else:
            quarters += 1
            curr_yr_earning += quarterly_earning_dict[key]
    # extrapolate the current quarters earnings (may be 1, 2 or 3 quarters)
    # to the entire year. This has an assumption that the current trend in
    # earning will continue for the entire year.
    curr_yr_quarterly_avg = curr_yr_earning / quarters
    curr_yr_earning = curr_yr_quarterly_avg * 4

    if latest_date.year - num_yrs in annual_earning_dict:  # i.e. if (key) in (dict)
        earning_start_year = annual_earning_dict[latest_date.year - num_yrs]
    else:
        # Earning that long back does not exist
        return 0
    if 0.0 == earning_start_year:
        return 0

    cumulative_growth = float(((curr_yr_earning - earning_start_year) / earning_start_year) * 100)
    return cumulative_growth


def get_long_term_debt(ticker):
    url = get_long_term_debt_url(ticker, snp500[ticker])
    soup = get_html(url)
    body = soup.find("body")
    tables = body.find_all("table")

    # We only store debt values every quarter. Since debt latest quarter is the total anyways
    # and does not add/subtract (or has anything to do) with the debt in past quarter.
    total_quarterly_long_term_debt_dict = extract_table(tables, 'Quarterly Long Term Debt')
    if total_quarterly_long_term_debt_dict == 'NAN':
        WARNING("Unable to get current asset")
        return 'NAN'

    latest_date = list(total_quarterly_long_term_debt_dict.keys())[0]
    return total_quarterly_long_term_debt_dict[latest_date]


# input:
#       total_assets - float value
#       liabilities  - float value
# return:
#       net assets   - float value
# NOTE: Net Assets is also known as working capital
def cal_net_assets(total_assets, liabilities):
    return float(float(total_assets) - float(liabilities))


def extract_snp500_list():
    soup = get_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    body = soup.find("body")
    tables = body.find_all("table")
    table = tables[0]
    table_rows = table.find_all('tr')

    snp500_dict = {}
    dividend_yield_dict = {}

    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        # print(row)
        if len(row) == 9:
            symbol = str(row[0].split('\n')[0])
            name = str(row[1]).split(' Inc')[0].split(' Corp')[0].split(' Co')[0].split(' plc')[0].split(' ,')[0]
            name = name.replace(' ', '-')
            snp500_dict[symbol] = name
    for key in snp500_dict:
        print("'" + key + "'" + ': ' + "'" + snp500_dict[key] + "',")


def test(ticker):
    print("current asset: " + str(get_total_curr_asset_value(ticker)))
    # print("liabilities: " + str(get_total_curr_liabilities(ticker)))
    # print("long term debt: " + str(get_long_term_debt(ticker)))
    # print("Shares outstanding: " + str(get_shares_outstanding(ticker)))