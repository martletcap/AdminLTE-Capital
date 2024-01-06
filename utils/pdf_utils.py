import re
import string

import PyPDF2

def shareholders_from_pdf(pdf):
    if pdf.content_type != 'application/pdf':
        return None, []
    reader = PyPDF2.PdfReader(pdf, strict=False)
    page = reader.pages[0].extract_text()
    company_name =  re.search(r'Company Name:\s(.+)(?:\s+|$)', page).group(1)
    # company_number =  re.search(r'Company Number:\s(.+)(?:\s+|$)', page).group(1)
    if not company_name: raise Exception('Unsupported file')

    res = []
    # Helper set
    printable = set(string.ascii_letters + string.digits + string.punctuation + ' ')
    pattern = re.compile((
            r'Shareholding\s(?:[0-9]+):\s([0-9]+)\s([0-9A-Z\s\n\W]+)\s[a-z\s\n]+'
            r'(?:Electronically\sfiled\sdocument\sfor\sCompany\sNumber:\s(?:[0-9]+))?'
            r'Name:\s([0-9A-Z\s\n\W]+)\n'
    ))
    text = ''
    for page in reader.pages:
        text +=  page.extract_text()
        
    for group in pattern.finditer(text):
        tmp = []
        for match in group.groups():
            # Deleting all escape sequence characters
            tmp.append(''.join(letter for letter in match if letter in printable))
        res.append(tmp)
    return(company_name, res)