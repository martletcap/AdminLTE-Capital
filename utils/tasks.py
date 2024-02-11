from celery import shared_task

from utils.parsing import last_company_file_items, item_to_shareholder_list
from home.models import Company, CompanyHouseParser


@shared_task
def parse_all_shareholders():
    companies = Company.objects.filter(
        category = 1 # Only "Companys" category
    )
    for company in companies:
        items = last_company_file_items(company)
        for item in items:
            parser_record = CompanyHouseParser(
                company = company,
                transaction_id = item['id'],
                file_date = item['date'],
            )
            res_shareholder_list = item_to_shareholder_list(
                company,
                item,
                parser_record,
            )
            parser_record.shareholder_list = res_shareholder_list
            parser_record.save()
       
@shared_task
def parse_company_shareholders(id):
    company = Company.objects.get(id=id)
    items = last_company_file_items(company)
    for item in items:
        parser_record = CompanyHouseParser(
            company = company,
            transaction_id = item['id'],
            file_date = item['date'],
        )
        res_shareholder_list = item_to_shareholder_list(
            company,
            item,
            parser_record,
        )
        parser_record.shareholder_list = res_shareholder_list
        parser_record.save()
            


