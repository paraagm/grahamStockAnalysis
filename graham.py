
from myUTL import *
from myUTL import _print


# Graham's test insists on "some earnings" for the common stock in
# each of the past 10 years
# Return 1 if PASS.
def graham_earning_stability(eps_history, start_year=10):
    annual_eps_dict = eps_history["annual"]
    curr_date = date.today()
    yr = curr_date.year - 1
    res = 1
    for i in range(0, start_year):
        if yr-i in annual_eps_dict:
            if annual_eps_dict[yr-i] < 0:
                _print("Negative earning: " + str(yr-i) + ": $" + str(annual_eps_dict[yr-i]))
                res = 0
        else:
            # key is not in dict i.e. year is not in the eps history
            res = 0
    return res


# Graham's earning growth is measured in 10 year cumulative
# in - cumulative_growth_cutoff: % value
# Returns 1 if cumulative growth is greater that the cutoff
def graham_earning_growth(eps_history, cumulative_growth_cutoff=33, num_yrs=10):
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
    curr_yr_quarterly_avg = curr_yr_earning/quarters
    curr_yr_earning = curr_yr_quarterly_avg * 4

    if latest_date.year - num_yrs in annual_earning_dict:   # i.e. if (key) in (dict)
        earning_start_year = annual_earning_dict[latest_date.year - num_yrs]
    else:
        # Earning that long back does not exist
        return 0
    if 0.0 == earning_start_year:
        return 0

    cumulative_growth = float(((curr_yr_earning - earning_start_year)/earning_start_year)*100)
    _print(str(num_yrs) + " yr Cumulative growth: " + str(cumulative_growth) + "%")

    if cumulative_growth > cumulative_growth_cutoff:
        return 1
    else:
        return 0


# Company should have some dividend payout for the last 20 years
def graham_dividend_record(dividend_history, num_years=20):
    result = 1
    dividend_amt_dict = dividend_history["dividend_amt"]
    target_year = date.today().year - num_years  # Till this year the company should have some dividend payouts
    if dividend_amt_dict.__len__() == 0:
        # No dividend history
        return 0

    first_dividend_payout_quarter = list(dividend_amt_dict.keys())[dividend_amt_dict.__len__()-1]
    if first_dividend_payout_quarter.year > target_year:
        # Not long enough dividend history
        return 0

    curr_year = date.today().year
    for key in dividend_amt_dict:
        quarter_date = key
        if (quarter_date.year == curr_year and dividend_amt_dict[quarter_date] > 0):
            curr_year -= 1  # This year there is a dividend pay out. Decrement to check the next "previous" year
    if curr_year <= target_year:
        return 1
    else:
        return 0


# Graham recommends limiting yourself to stocks whose current
# price is no more than 15 times average earnings.
# In here, we calculate average earnings over 7 years
def graham_pe_ratio(pe_ratio, cutoff=15):
    if int(pe_ratio) < cutoff and pe_ratio > 0.0:
        return 1
    else:
        return 0



# Book value or net assets = Total assets - total liabilities
# Book value per share = book value / total number of shares
# P/B ratio = Share price / Book value per share
# According to Graham, Total assets should be at least twice the liabilities.
# P/B ratio should be 1.5 ==> This means that a healthy company's book value (net assets) must be
#                             at least half of it's market cap.
def graham_pb_ratio(pb_ratio, threshold=1.5):
    if pb_ratio > float(threshold) or pb_ratio < 0.0:
        return 0
    return 1


# Graham's market cap for the companies is minimum of 2 Billion
# This function must get market cap float value in billions
def graham_market_cap(market_cap):
    if market_cap < float(2.0):
        return 0
    return 1


# input:
#   total_asset - float
#   liabilities - float
#   long_term_debt - float
# Current assets should be at least twice current liabilities
# Also long-term debt should not exceed the net current asset (i.e. working capital)
def graham_financial_condition(financial_data, asset_to_liab_ratio=2.0, debt_to_asset_ratio=1.0):
    total_asset = financial_data["total_assets"]
    liabilities = financial_data["liabilities"]
    long_term_debt = financial_data["long_term_debt"]
    if 'NAN' == total_asset or 'NAN' == liabilities or 'NAN' == long_term_debt:
        # Financial data is not completely available to make this analysis
        return 0

    if(float(total_asset) > float(liabilities*asset_to_liab_ratio)) and\
            (cal_net_assets(total_asset, liabilities)*debt_to_asset_ratio > long_term_debt):
        return 1
    else:
        return 0


def graham_analysis_defensive(company_ticker):
    result = ''
    financial_data = {"total_assets": get_total_curr_asset_value(company_ticker),
                      "liabilities": get_total_curr_liabilities(company_ticker),
                      "long_term_debt": get_long_term_debt(company_ticker)}
    stock_price = get_stock_price(company_ticker)

    # Financial stability
    _print("total assets: " + str(financial_data["total_assets"]))
    _print("liabilities: " + str(financial_data["liabilities"]))
    _print("lon_term_debt: " + str(financial_data["long_term_debt"]))
    if graham_financial_condition(financial_data):
        _print("Good financial condition")
        result += 'P,'
    else:
        _print("Financial condition not good")
        result += 'F,'

    # Market cap
    market_cap = get_market_cap(company_ticker)
    if graham_market_cap(market_cap):
        _print("Market cap: " + str(market_cap))
        result += 'P,'
    else:
        _print("Company size id small: " + str(market_cap))
        result += 'F,'

    # P/B ratio
    pb_ratio = get_pb_ratio(company_ticker, financial_data, stock_price)
    if graham_pb_ratio(pb_ratio):
        _print("PB ratio PASS")
        result += 'P,'
    else:
        _print("PB ratio FAIL: " + str(pb_ratio))
        result += 'F,'

    # P/E ratio
    eps_history = get_eps_history(company_ticker)
    result = result + 'P,' if 1 == graham_pe_ratio(eps_history, get_stock_price(company_ticker)) else result + 'F,'

    # Dividend related
    dividend = get_divided_yield_history(company_ticker)
    if graham_dividend_record(dividend):
        _print("Dividend record PASS")
        result = result + 'P,'
    else:
        _print("Dividend record FAIL")
        result += 'F,'

    # EPS related
    result = result + 'P,' if 1 == graham_earning_stability(eps_history) else result + 'F,'

    result = result + 'P' if 1 == graham_earning_growth(eps_history, 33) else result + 'F'

    return result


# Analyze company using Graham's Enterprise criterion.
# Result format:
#       assets | liabilities | debt | Financial stability Result |
#       Market Cap | Result |
#       P/B        | Result |
#       P/E        | Result | Max Fair price | Current price
#       Dividend stability result
#       Earning stability result
#       Earning growth Result
def graham_analysis_enterprise(company_ticker):
    result = ''
    financial_data = {"total_assets": get_total_curr_asset_value(company_ticker),
                      "liabilities": get_total_curr_liabilities(company_ticker),
                      "long_term_debt": get_long_term_debt(company_ticker)}
    stock_price = get_stock_price(company_ticker)

    # Financial stability
    _print("total assets: " + str(financial_data["total_assets"]))
    _print("liabilities: " + str(financial_data["liabilities"]))
    _print("lon_term_debt: " + str(financial_data["long_term_debt"]))
    result += str(financial_data["total_assets"]) + ',' + str(financial_data["liabilities"]) + ',' + str(financial_data["long_term_debt"]) + ','
    # Current assets at least 1.5 times liabilities. Debt not more that 110% net current asset.
    if graham_financial_condition(financial_data, 1.5, 1.1):
        _print("Good financial condition\n")
        result += 'P,'
    else:
        _print("Financial condition not good\n")
        result += 'F,'

    # Market cap
    market_cap = get_market_cap(company_ticker)
    result += str(market_cap) + ','
    if graham_market_cap(market_cap):
        _print("Market cap: " + str(market_cap) + "\n")
        result += 'P,'
    else:
        _print("Company size id small: " + str(market_cap) + "\n")
        result += 'F,'

    # P/B ratio
    pb_ratio = get_pb_ratio(company_ticker, financial_data, stock_price)
    result += str(pb_ratio) + ','
    if graham_pb_ratio(pb_ratio, 1.2):
        _print("PB ratio PASS: " + str(pb_ratio) + "\n")
        result += 'P,'
    else:
        _print("PB ratio FAIL: " + str(pb_ratio) + "\n")
        result += 'F,'

    # P/E ratio
    eps_history = get_eps_history(company_ticker)
    num_avg_years = 5
    pe_ratio = get_pe_ratio(company_ticker, eps_history, num_avg_years, stock_price)
    result += str(pe_ratio) + ','
    if graham_pe_ratio(pe_ratio, 25):
        _print("PE ratio PASS: " + str(pe_ratio) + "\n")
        result += 'P,'
    else:
        _print("PE ratio FAIL: " + str(pe_ratio) + "\n")
        result += 'F,'

    # Max Fair stock price according to PE ratio
    result += str(get_max_pe_fair_price(company_ticker, eps_history, num_avg_years, 25)) + ','

    # Current stock price
    result += str(stock_price) + ','

    # Dividend related
    dividend = get_divided_yield_history(company_ticker)
    if graham_dividend_record(dividend, 5):
        _print("Dividend record PASS")
        result = result + 'P,'
    else:
        _print("Dividend record FAIL")
        result += 'F,'

    # EPS related
    # No deficit in last 5 years
    result = result + 'P,' if 1 == graham_earning_stability(eps_history, 5) else result + 'F,'
    # NOTE: Earning growth criteria is not clear in the book. So This is my own.
    # Defensive analysis requires 33% in 10 years. That is 3% per year. So for 5 years, 16% (roughly)
    result = result + 'P' if 1 == graham_earning_growth(eps_history, 16, 5) else result + 'F'

    return result
