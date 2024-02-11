import os
from io import BytesIO
from django.db.models import F
from datetime import datetime, date
from collections import defaultdict

import requests
from dotenv import load_dotenv

from utils.pdf_utils import CS01_parser, SH01_parser
from home.models import (
    ContactType, Contact, ShareType, Share, ShareholderList, Shareholder,
    CompanyHouseParser,
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
        data = response.json()
        # Check credentials
        assert response.status_code != 401, 'Invalid COMPANY_HOUSE_KEY!'
        assert response.ok == True, 'Company House parsing error!'

        items = data['items']
        if len(items)<items_per_page: parse = False
        for item in items:
            item_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
            if item_date<last_date:
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
    # Only files newer than 2024 01 01
    last_date = date(2024, 1, 1)
    last_parsing_date = CompanyHouseParser.objects.filter(
        company = company
    ).order_by('-file_date').first()
    if last_parsing_date:
        last_date = max(last_date, last_parsing_date.file_date)
    
    items = company_filling_history(company.number, last_date)
    # Sorting from minimum to maximum date
    return sorted(items, key=lambda x: x['date'])

def item_to_shareholder_list(company, item, parser_record):
    cur_shareholder_list = None
    file = company_house_pdf(company.number, item['id'])
    # CS01 behavior
    if item['type'] == 'CS01':
        try:
            _, res, date = CS01_parser(file)
        except:
            parser_record.comment = 'Unsupported file format.'
            return
        if not res:
            parser_record.comment = 'ShareholderList file is empty.'
            return
        cur_shareholder_list, created = ShareholderList.objects.get_or_create(company=company, date=date)
        # If a ShareholderList already exists, do not create a new one
        if not created:
            parser_record.comment = 'ShareholderList already exists.'
            return
        for record in res:
            # Get or crate Contact
            contact, _ = Contact.objects.get_or_create(
                name = record['owner'],
                defaults={
                    'type':ContactType.objects.get(id=7) # No Type Info
                }
            )
            # Get or crate Share
            share_type, _ = ShareType.objects.get_or_create(
                type = record['share']
            )
            share, _ = Share.objects.get_or_create(type=share_type, company=company)
            # Create shareholder
            Shareholder.objects.create(
                shareholder_list = cur_shareholder_list,
                contact = contact,
                share = share,
                amount = record['amount'],
            )
    # SH01 behavior
    elif item['type'] == 'SH01':
        try:
            _, res, date = SH01_parser(file)
        except:
            parser_record.comment = 'Unsupported file format.'
            return
        # Total share amount
        share_amounts = defaultdict(int)
        for r in res:
            share = r['share'].replace(' SHARES', '')
            share_amounts[share]+= r['amount']
        # Prev shareholders
        shareholder_list = ShareholderList.objects.filter(
            company = company,
            date__lt = date,
        ).order_by('-date')[:1].first()
        shareholders = Shareholder.objects.filter(
            shareholder_list = shareholder_list,
        ).annotate(
            name = F('contact__name'),
            type = F('share__type__type'),
            contact_type = F('contact__type'),
        )
        # To copy
        records = []
        for shareholder in shareholders:
                if shareholder.option:
                    share_amounts[shareholder.type]-=shareholder.amount
                records.append({
                    'amount': shareholder.amount,
                    'type': shareholder.type,
                    'option': shareholder.option,
                    'contact':shareholder.contact
                })
        default_contact = Contact.objects.get(pk=1) # "No Name" contact
        for key, value in share_amounts.items():
            if value<0:
                parser_record.comment = 'Liquidation error!'
                return
            elif value>0:
                added = False
                # If the default_contact with the same share is
                # already in the database, add it to it; if not, create it.
                for record in records:
                    if (record['contact'] == default_contact and
                        record['type'] == key and
                        record['option'] == True):
                        record['amount']+=value
                        added = True
                        break
                if not added:
                    records.append({
                    'amount': value,
                    'type': key,
                    'option': True,
                    'contact':default_contact,
                    })
        cur_shareholder_list, created = ShareholderList.objects.get_or_create(company=company, date=date)
        # If a ShareholderList already exists, do not create a new one
        if not created:
            parser_record.comment = 'ShareholderList already exists.'
            return
        for record in records:
            share_type, _ = ShareType.objects.get_or_create(type=record['type'])
            share, _ = Share.objects.get_or_create(type=share_type, company = company)
            Shareholder.objects.create(
                shareholder_list = cur_shareholder_list,
                contact = record['contact'],
                share = share,
                amount = record['amount'],
                option = record['option'],
            )
    return cur_shareholder_list