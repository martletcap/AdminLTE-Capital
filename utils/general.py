import re


def share_name_correction(line:str):
    line = line.replace('SHARES', '')
    # Del smth like "0.0001 GBP..."
    line = line[0:line.find('0.')]
    # Del more then 2 spaces
    line = re.sub(' +', ' ', line)
    # Del spaces from start or end
    return line.strip()