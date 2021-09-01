
# local lib
from graham import *
from ticker import snp500
from time import perf_counter
import xlsxwriter

def snp500_enterpise_analysis():
    workbook = xlsxwriter.Workbook('snp500_enterprise.xlsx')
    worksheet = workbook.add_worksheet()
    # Start from the first cell.
    # Rows and columns are zero indexed.
    row = 0

    # Populate the heading row in the file
    heading = "Company Name ,Assets ,Liabilities ,Debt ,Financial Stability ,Market Cap , ,P/B, ,P/E, ,Max fair price ,Current price ,Dividend ,Earning ,Earning growth , ,Final Result"
    # Save to worksheet
    column_values = heading.split(',')
    column = 0
    for val in column_values:
        worksheet.write(row, column, val)
        column += 1
    row += 1

    for key in snp500:
        result = graham_analysis_enterprise(key)
        out = key + ": " + snp500[key] + "," + result
        print(out)
        # Save to worksheet
        column_values = out.split(',')
        column = 0
        for val in column_values:
            worksheet.write(row, column, val)
            column += 1
        row += 1

    #  Debug only
    # result = graham_analysis_enterprise("NVR")
    # out = "NVR" + ": " + snp500["NVR"] + "," + result
    # print(out)
    # # Save to worksheet
    # column_values = out.split(',')
    # column = 0
    # for val in column_values:
    #     worksheet.write(row, column, val)
    #     column += 1
    # row += 1

    workbook.close()


if __name__ == '__main__':
    # test('ABBV')
    start = perf_counter()
    result = graham_analysis_enterprise('AMZN')
    print(result)

    # snp500_enterpise_analysis()


    print("Elapsed time in sec:", perf_counter() - start)












