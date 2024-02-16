import re


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