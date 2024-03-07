from datetime import date
from collections import defaultdict

from home.models import (
    Company, Contact, ContactType, Share, ShareType, ShareholderList,
    Shareholder, SharePrice,
)
from utils.general import share_name_correction


def copy_shareholder_list(company, date):
    prev_shareholder_list = ShareholderList.objects.filter(
        company = company,
        date__lt = date,
    ).order_by('-date').first()
    # Checking that the previous list exists
    if not prev_shareholder_list:
        return None
    shareholder_list, created = ShareholderList.objects.get_or_create(
        company = company,
        date = date,
    )
    # Checking that the list with the current date
    # has not yet been created
    if not created:
        return None
    prev_shareholders = Shareholder.objects.filter(
        shareholder_list = prev_shareholder_list,
    )
    # Copy all objs
    for shareholder in prev_shareholders:
        shareholder.pk = None
        shareholder.shareholder_list = shareholder_list
        shareholder.save()
    
    return shareholder_list

def compare_shareholderlist(shareholder_list:ShareholderList, amounts:dict):
    shareholders = Shareholder.objects.filter(
        shareholder_list = shareholder_list,
        option = True,
    ).select_related('share__type')
    cur_amounts = defaultdict(int)
    for shareholder in shareholders:
        cur_amounts[shareholder.share.type.type]+=shareholder.amount

    for key, value in amounts.items():
        cur_amounts[key] -= value

    for value in cur_amounts.values():
        if value != 0:
            return False
    return True
    

def CS01_to_shareholderlist(shareholders:list, date:date, company:Company):
    default_contact_type = ContactType.objects.get(id=7) # No Type Info
    shareholder_list = ShareholderList.objects.create(
        company=company, date=date, comment = 'Created by parser.',
    )
    for record in shareholders:
        owner = record['owner']
        share_title = record['share']
        amount = record['amount']
        # Get or crate Contact
        contact, _ = Contact.objects.get_or_create(
            name = owner,
            defaults={'type':default_contact_type}
        )
        # Get or crate Share
        share_type, _ = ShareType.objects.get_or_create(
            type = share_name_correction(share_title),
        )
        share, _ = Share.objects.get_or_create(
            type = share_type,
            company = company,
        )
        # Create shareholder
        Shareholder.objects.create(
            shareholder_list = shareholder_list,
            contact = contact,
            share = share,
            amount = amount,
        )
    return shareholder_list

def SH01_to_shareholderlist(shares, date, company):
    # Total share amount
    share_amounts = defaultdict(int)
    for share in shares:
        # Correct name
        share_type = share_name_correction(share['share'])
        share_amounts[share_type] += share['amount']
    # Prev shareholders
    prev_shareholder_list = ShareholderList.objects.filter(
        company = company,
        date__lt = date,
    ).order_by('-date').first()
    prev_shareholders = Shareholder.objects.filter(
        shareholder_list = prev_shareholder_list
    ).select_related(
        'share__type', 'contact__type',
    )
    # To copy
    new_records = []
    for shareholder in prev_shareholders:
        if shareholder.option:
            share_amounts[shareholder.share.type.type] -= shareholder.amount
        new_records.append({
            'amount': shareholder.amount,
            'type': shareholder.share.type.type,
            'option': shareholder.option,
            'contact': shareholder.contact,
        })
    default_contact = Contact.objects.get(pk=1) # "No Name" contact
    for key, value in share_amounts.items():
        if value<0:
            return None
        elif value>0:
            added = False
            # If the default_contact with the same share is
            # already in the new list, add it to it; if not, create it.
            for record in new_records:
                if (record['contact'] == default_contact and
                    record['type'] == key and
                    record['option'] == True):
                    record['amount']+=value
                    added = True
                    break
            if not added:
                new_records.append({
                'amount': value,
                'type': key,
                'option': True,
                'contact':default_contact,
                })
    new_shareholder_list = ShareholderList.objects.create(
        company = company, date = date, comment = 'Created by parser.',
    )
    for record in new_records:
        share_type, _ = ShareType.objects.get_or_create(type=record['type'])
        share, _ = Share.objects.get_or_create(type=share_type, company=company)
        Shareholder.objects.create(
            shareholder_list = new_shareholder_list,
            contact = record['contact'],
            share = share,
            amount = record['amount'],
            option = record['option'],
        )
    return new_shareholder_list

def is_new_shares(res, company):
    new_shares = []
    for r in res:
        share_name = share_name_correction(r['share'])
        exists = Share.objects.filter(
            company = company,
            type__type = share_name
        ).exists()
        if not exists:
            new_shares.append(share_name)

    return new_shares