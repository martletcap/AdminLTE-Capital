from celery import shared_task

from utils.parsing import last_company_file_items, item_to_shareholder_list
from home.models import Company, CompanyHouseParser


@shared_task
def parse_all_shareholders(**filters):
    companies = Company.objects.filter(
        category = 1, # Only "Companys" category
        **filters,
    )
    for company in companies:
        items = last_company_file_items(company)
        for item in items:
            parser_record = CompanyHouseParser(
                company = company,
                transaction_id = item['id'],
                file_date = item['date'],
            )
            res_shareholder_list, message = item_to_shareholder_list(
                company,
                item,
            )
            parser_record.comment = message
            parser_record.shareholder_list = res_shareholder_list
            parser_record.save()
            # if there is an error, do not check the following files
            # for this company
            if res_shareholder_list is None:
                break