import re

import PyPDF2

def shareholders_from_pdf(pdf: str):
    if pdf.content_type != 'application/pdf':
        return None, []
    reader = PyPDF2.PdfReader(pdf, strict=False)
    page = reader.pages[0].extract_text()
    company_name =  re.search(r'Company Name:\s(.+)(?:\s+|$)', page).group(1)
    # company_number =  re.search(r'Company Number:\s(.+)(?:\s+|$)', page).group(1)
    if not company_name: raise Exception('Unsupported file')

    res = []
    for page in reader.pages:
        text = page.extract_text()
        pattern = re.compile((
            r'Shareholding\s(?:[0-9]+):\s([0-9]+)\s([A-Z\s\n\W]+)\s[a-z\s\n]+'
            r'Name:\s([A-Z\s\n\W]+)\n'
        ))
        res.extend(pattern.findall(text))
    for _, _, owner in res:
        owner = owner.replace('\n', '')
    return(company_name, res)