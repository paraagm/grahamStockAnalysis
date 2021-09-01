
eps_url            = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/eps-earnings-per-share-diluted'
dividend_url_nasdaq= 'https://www.marketbeat.com/stocks/NASDAQ/<ticker_sym>/dividend/'
dividend_url_nyse  = 'https://www.marketbeat.com/stocks/NYSE/<ticker_sym>/dividend/'
stock_price_url    = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/stock-price-history'
PtoB_ratio_url     = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/price-book'
market_cap_url     = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/market-cap'
total_asset_url    = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/total-assets'
liabilities_url    = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/total-liabilities'
long_term_debt_url = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/long-term-debt'
shares_outstanding_url = 'https://www.macrotrends.net/stocks/charts/<ticker_sym>/<ticker_name>/shares-outstanding'


def get_eps_url(ticker_sym, ticker_name):
    data = eps_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_dividend_url_nasdaq(ticker_sym, ticker_name):
    data = dividend_url_nasdaq.split('<ticker_sym>')
    url = data[0] + str(ticker_sym) + data[1]
    return url


def get_dividend_url_nyse(ticker_sym, ticker_name):
    data = dividend_url_nyse.split('<ticker_sym>')
    url = data[0] + str(ticker_sym) + data[1]
    return url


def get_price_url(ticker_sym, ticker_name):
    data = stock_price_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_pb_ratio_url(ticker_sym, ticker_name):
    data = PtoB_ratio_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_market_cap_url(ticker_sym, ticker_name):
    data = market_cap_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_total_asset_url(ticker_sym, ticker_name):
    data = total_asset_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_liabilities_url(ticker_sym, ticker_name):
    data = liabilities_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_long_term_debt_url(ticker_sym, ticker_name):
    data = long_term_debt_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url


def get_shares_outstanding_url(ticker_sym, ticker_name):
    data = shares_outstanding_url.split('<ticker_sym>/<ticker_name>')
    url = str(data[0]) + str(ticker_sym) + '/' + str(ticker_name) + str(data[1])
    return url
