import re
from datetime import datetime, timedelta
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

def previous_quarters(n):
    first_month_of_quarter = {1:1, 2:4, 3:7, 4:10}

    current_date = datetime.now()
    current_quarter = current_date.month//4+1
    prev_quarter = datetime(
        current_date.year, first_month_of_quarter[current_quarter], 1,
    )

    quarter_offset = 0
    while n>quarter_offset:
        date_lt = prev_quarter - relativedelta(months=3*quarter_offset)
        date_gte = prev_quarter - relativedelta(months=3*(quarter_offset+1))
        yield date_gte, date_lt
        quarter_offset+=1

def get_fiscal_quarter(date):
    fiscal_date = date - relativedelta(months=3)
    return f'{fiscal_date.year}Q{fiscal_date.month//3+1}'