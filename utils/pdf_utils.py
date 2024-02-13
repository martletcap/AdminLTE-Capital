import re
import string
from datetime import datetime

import PyPDF2
from PyPDF2.errors import PyPdfError

def line_correction(line:str):
    printable = set(string.ascii_letters + string.digits + string.punctuation + ' ')
    return ''.join(letter for letter in line if letter in printable)

def CS01_parser(pdf):
    reader = PyPDF2.PdfReader(pdf, strict=False)
    res = []
    # Pattern
    pattern = re.compile((
            r'Shareholding\s(?:[0-9]+):\s([0-9]+)\s([0-9A-Z\s\n\W]+)\s[a-z\s\n]+'
            r'Name:\s([0-9A-Z\s\n\W]+)\n'
    ))
    # Concat text
    text = ''
    for page in reader.pages:
        text +=  page.extract_text()

    company_number =  re.search(r'Company Number:\s(.+)(?:\s+|$)', text).group(1)
    date = re.search(r'Statement date:(\d{2}/\d{2}/\d{4})', text).group(1)
    date = datetime.strptime(date, '%d/%m/%Y').date()

    # Remove problem areas
    text = re.sub(r'Electronically\sfiled\sdocument\sfor\sCompany\sNumber:\s(?:[0-9]+)', '', text)
    text = re.sub(r'\d+\stransferred\son\s\d+-\d+-\d+\s', '', text)

    for match in pattern.finditer(text):
        amount = line_correction(match.group(1))
        share = line_correction(match.group(2))
        owner = line_correction(match.group(3))
        res.append({
            'amount': amount,
            'share': share,
            'owner': owner,
        })
    return(company_number, res, date)

def SH01_parser(pdf):
    reader = PyPDF2.PdfReader(pdf, strict=False)
    res = []
    # Pattern
    pattern = re.compile((
            r'Class\sof\sShares:\s([A-Z0-9\W]+)Currency:'
            r'.+Number\sallotted\s(\d+)'
    ))
    # Concat text
    text = ''
    for page in reader.pages:
        text +=  page.extract_text()

    company_number =  re.search(r'Company Number:\s(.+)(?:\s+|$)', text).group(1)
    date = re.search(r'allottedFrom To\s(\d{2}/\d{2}/\d{4})', text).group(1)
    date = datetime.strptime(date, '%d/%m/%Y').date()
    
    # Remove problem areas
    text = text[text.find('Statement of Capital (Share Capital)'):]

    for match in pattern.finditer(text):
        share = line_correction(match.group(1))
        amount = line_correction(match.group(2))
        res.append({
            'share': share,
            'amount': amount,
        })
    return(company_number, res, date)

def report_file_name(pdf):
    try:
        reader = PyPDF2.PdfReader(pdf, strict=False)
    except PyPdfError:
        return
    page = reader.pages[0].extract_text()
    match = re.search(r'([0-9A-Z]{4})\s\(ef\)', page)
    if match:
        return match.group(1)