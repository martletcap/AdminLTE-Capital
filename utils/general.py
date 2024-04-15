import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


def share_name_correction(line:str):
    line = line.replace('SHARES', '')
    line = line.replace('(NON-VOTING)', '')
    # Del smth like "0.0001 GBP..."
    flt = line.find('0.')
    if flt != -1:
        line = line[0:flt]
    # Del more then 2 spaces
    line = re.sub(' +', ' ', line)
    # Del spaces from start or end
    return line.strip()

def previous_quarters(number, start_date=None):
    # Find the first month of the current quarter
    first_month_of_quarter = {1:1, 2:4, 3:7, 4:10}
    if start_date is None:
        start_date = datetime.now()
    current_quarter = start_date.month//4 + 1
    cur_quarter_start_month = first_month_of_quarter[current_quarter]

    # First date of the next quarter
    first_date_lt = datetime(
        start_date.year, first_month_of_quarter[current_quarter], 1,
    ) + relativedelta(months=3)

    quarter_offset = 0
    while number>quarter_offset:
        date_lt = first_date_lt - relativedelta(months=3*quarter_offset)
        date_gte = first_date_lt - relativedelta(months=3*(quarter_offset+1))
        date_lte = date_lt - relativedelta(days=1)
        yield date_gte, date_lte
        quarter_offset+=1

def get_fiscal_quarter(date):
    fiscal_date = date - relativedelta(months=9)
    return f'{fiscal_date.year}Q{fiscal_date.month//3+1}'