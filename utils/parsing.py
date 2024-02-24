import os
from io import BytesIO
from datetime import datetime, date
from collections import defaultdict

import requests
from dotenv import load_dotenv

from utils.pdf_utils import CS01_parser, SH01_parser
from utils.model import (
    copy_shareholderlist, compare_shareholderlist, CS01_to_shareholderlist,
    SH01_to_shareholderlist, non_existent_variants_list,
    convert_shares_to_share_types,
)
from home.models import (
    ShareholderList, CompanyHouseParser
)


load_dotenv()
COMPANY_HOUSE_KEY = os.getenv('COMPANY_HOUSE_KEY')

def company_filling_history(
        company_number,
        last_date,
        items_per_page=100,
        supported_file_types = {'CS01', 'SH01'},
    ):
    link = 'https://api.companieshouse.gov.uk/company/{0}/filing-history'
    result = []

    params = {
        'category': 'confirmation-statement,capital',
        'items_per_page': items_per_page,
        'start_index': 0,
    }
    headers = {
        'Authorization': COMPANY_HOUSE_KEY
    }

    # Iterate switch
    parse = True
    while parse:
        response = requests.get(
            link.format(company_number),
            params=params, headers=headers
        )
        # Check credentials
        assert response.status_code != 401, 'Invalid COMPANY_HOUSE_KEY!'
        assert response.ok == True, 'Company House parsing error!'
        data = response.json()

        items = data['items']
        if len(items)<items_per_page: parse = False
        for item in items:
            item_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
            if item_date<=last_date:
                parse = False
                break
            if item['type'] not in supported_file_types:
                continue
            result.append({
                'date': item_date,
                'type': item['type'],
                'id': item['transaction_id'],
            })
        # Shift the list
        params['start_index'] += items_per_page
    return result
    
def company_house_pdf(company_number, transaction_id):
    file_link = 'https://find-and-update.company-information.service.gov.uk/company/{0}/filing-history/{1}/document?format=pdf'
    response = requests.get(file_link.format(company_number, transaction_id))
    return BytesIO(response.content)

def last_company_file_items(company):
    # Only files newer than 2023 10 1
    last_date = date(2023, 10, 1)
    last_parsing = CompanyHouseParser.objects.filter(
        company = company
    ).order_by('-file_date', '-id').first()
    if last_parsing:
        # if the previous error has not been corrected,
        # do not parse further files
        if last_parsing.shareholder_list is None:
            return []
        last_date = max(last_date, last_parsing.file_date)
    
    items = company_filling_history(company.number, last_date)
    # Sorting from minimum to maximum date
    return sorted(items, key=lambda x: x['date'])

def item_to_shareholder_list(company, item):
    file = company_house_pdf(company.number, item['id'])

    res = []
    date = None
    # CS01 - shareholder list
    # SH01 - list of shares
    if item['type'] == 'CS01':
        try:
            _, res, date = CS01_parser(file)
        except:
            return None, 'Unsupported file format.'
    elif item['type'] == 'SH01':
        try:
            _, res, date = SH01_parser(file)
        except:
            return None, 'Unsupported file format.'
        
    shareholder_list = ShareholderList.objects.filter(
        company = company,
        date = date,
    ).order_by('-id').first()

    # Checking that all share variants are already in the database
    distressed_shares = non_existent_variants_list(res)
    if len(distressed_shares) != 0:
        comment = f'Non-existent stock options: {", ".join(distressed_shares)}'
        return None, comment
    
    # Convert all share_name to ShareType instances
    res = convert_shares_to_share_types(res)

    # The list already exists but there are results
    if shareholder_list and res:
        # If the sheet matches, return it; if not, throw an error.
        tmp = defaultdict(int)
        for i in res:
            tmp[i['share']]+=i['amount']
        if compare_shareholderlist(shareholder_list, tmp):
            return shareholder_list, ''
        return None, 'A list for this date already exists.'
    # There is no list and results
    elif not shareholder_list and not res:
        # Copy last existing or return an error
        new_list = copy_shareholderlist(company, date)
        return new_list, ''
    # There is no sheet and there are results.
    elif not shareholder_list and res:
        new_list = None
        comment = ''
        # CS01 - create new
        if item['type'] == 'CS01':
            new_list = CS01_to_shareholderlist(res, date, company)
        # SH01 - expande previous
        elif item['type'] ==  'SH01':
            new_list = SH01_to_shareholderlist(res, date, company)
            if not new_list:
                comment = 'Liquidation error!'
        return new_list, comment
    # The list exists and the results are empty
    elif shareholder_list and not res:
        # Return an existing sheet
        return shareholder_list, ''