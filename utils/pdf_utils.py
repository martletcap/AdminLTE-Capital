import re
import string
from datetime import datetime

import PyPDF2

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

    company_name =  re.search(r'Company Name:\s(.+)(?:\s+|$)', text).group(1)
    date = re.search(r'Statement date:(\d{2}/\d{2}/\d{4})', text).group(1)
    date = datetime.strptime(date, '%d/%m/%Y').date()

    # Remove problem areas
    text = re.sub(r'Electronically\sfiled\sdocument\sfor\sCompany\sNumber:\s(?:[0-9]+)', '', text)
    text = re.sub(r'\d+\stransferred\son\s\d+-\d+-\d+\s', '', text)

    for match in pattern.finditer(text):
        res.append({
            'amount': int(line_correction(match.group(1))),
            'share': line_correction(match.group(2)),
            'owner': line_correction(match.group(3)),
        })
    return(company_name, res, date)

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

    company_name =  re.search(r'Company Name:\s(.+)(?:\s+|$)', text).group(1)
    date = re.search(r'allottedFrom To\s(\d{2}/\d{2}/\d{4})', text).group(1)
    date = datetime.strptime(date, '%d/%m/%Y').date()

    # Remove problem areas
    text = text[text.find('Statement of Capital (Share Capital)'):]

    for match in pattern.finditer(text):
        res.append({
            'share': line_correction(match.group(1)),
            'amount': int(line_correction(match.group(2))),
        })
    return(company_name, res, date)

def report_file_name(pdf):
    if pdf.content_type != 'application/pdf':
        return None
    reader = PyPDF2.PdfReader(pdf, strict=False)
    page = reader.pages[0].extract_text()
    match = re.search(r'([0-9A-Z]{4})\s\(ef\)', page)
    if match:
        return match.group(1)