from datetime import date
from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, resolve_url, redirect
from django.db.models import (
    F, Sum,
)

from utils.pdf_utils import CS01_parser, SH01_parser, report_file_name
from utils.general import share_name_correction, previous_quarters, get_fiscal_quarter
from home.models import (
    Company, ContactType, Contact, Share, MoneyTransaction, ShareTransaction,
    SharePrice, Split, ShareholderList, Shareholder, FairValueMethod,
)
from report.forms import (
    UploadFileForm, ShareholderListExtraForm, CompanySelectForm,
    ShareholderUploadFormSet, SharePriceFormSet, PeriodForm, DateForm,
    SharesControlFormSet,
)


def short_report(request):
    context = {}
    context['result_headers'] = [
        'Area', 'No. Com.', 'Pct. Com.', 'Investment', 'Investment Pct.',
        'Market Price', 'Market Price Pct.'
    ]
    sectors = {}
    locations = {}
    template = {
        'num': 0,
        'investment': 0,
        'market': 0,
    }

    # Get companies
    companies = Company.objects.filter(
        status = 1, # Portfolio status
    ).annotate(
        area = F('sector__name'),
        city = F('location__city')
    )
    total_companies = 0
    # Count companies by sector and city
    for company in companies:
        if not sectors.get(company.area):
            sectors[company.area]=template.copy()
        if not locations.get(company.city):
            locations[company.city]=template.copy()
        sectors[company.area]['num']+=1
        locations[company.city]['num']+=1
        total_companies += 1
    # Get money transactions
    money_transactions = MoneyTransaction.objects.filter(
        company__in = companies,
        portfolio__name = 'Martlet',
    ).annotate(
        area = F('company__sector__name'),
        city = F('company__location__city'),
        type = F('transaction_type__title'),
    )
    total_money_invested = 0
    # Sum all investments
    for transaction in money_transactions:
        if transaction.type == 'Sell':
            price = -float(transaction.price)
        else:
            price = float(transaction.price)
        total_money_invested += price
        sectors[transaction.area]['investment']+=price
        locations[transaction.city]['investment']+=price
    # Get share transactions
    share_transactions = ShareTransaction.objects.filter(
        money_transaction__company__in = companies,
    ).annotate(
        type = F('money_transaction__transaction_type__title'),
        area = F('money_transaction__company__sector__name'),
        city = F('money_transaction__company__location__city'),
    )
    total_market_price = 0
    # Sum market price
    for transaction in share_transactions:
        last_price = SharePrice.objects.last_price(share=transaction.share)
        cof = Split.objects.cof(
            date__gte = transaction.date,
            share=transaction.share,
        )
        if transaction.type == 'Sell':
            total = -float(transaction.amount*cof*last_price)
        else:
            total = float(transaction.amount*cof*last_price)
        total_market_price += total
        sectors[transaction.area]['market']+=total
        locations[transaction.city]['market']+=total
    # Representation
    context['results_sector'] = []
    context['results_location'] = []
    context['sectors'] = []
    context['locations'] = []
    context['chart1'] = []
    context['chart2'] = []
    context['chart3'] = []
    context['chart4'] = []
    context['chart5'] = []
    context['chart6'] = []
    for key in sectors.keys():
        company_pct = 0
        investment_pct = 0
        market_price_pct = 0
        if total_companies and sectors[key]['num']:
            company_pct = 100/total_companies*sectors[key]['num']
        if total_money_invested and sectors[key]['investment']:
            investment_pct = 100/total_money_invested*sectors[key]['investment']
        if total_market_price and sectors[key]['market']:
            market_price_pct = 100/total_market_price*sectors[key]['market']
        context['results_sector'].append((
            key, sectors[key]['num'],
            round(company_pct, 1),
            int(sectors[key]['investment']),
            round(investment_pct, 1),
            int(sectors[key]['market']),
            round(market_price_pct, 1),
        ))
        context['sectors'].append(key)
        context['chart1'].append(sectors[key]['num'])
        context['chart3'].append(sectors[key]['investment'])
        context['chart5'].append(sectors[key]['market'])
    for key in locations.keys():
        company_pct = 0
        investment_pct = 0
        market_price_pct = 0
        if total_companies and locations[key]['num']:
            company_pct = 100/total_companies*locations[key]['num']
        if total_money_invested and locations[key]['investment']:
            investment_pct = 100/total_money_invested*locations[key]['investment']
        if total_market_price and locations[key]['market']:
            market_price_pct = 100/total_market_price*locations[key]['market']
        context['results_location'].append((
            key, locations[key]['num'], 
            round(company_pct, 1),
            int(locations[key]['investment']),
            round(investment_pct, 1),
            int(locations[key]['market']),
            round(market_price_pct, 1),
        ))
        context['locations'].append(key)
        context['chart2'].append(locations[key]['num'])
        context['chart4'].append(locations[key]['investment'])
        context['chart6'].append(locations[key]['market'])
    # Footer-total
    context['footer'] = [
        'Total:', total_companies, 100, int(total_money_invested),
        100, int(total_market_price), 100,
    ]
    return render(request, 'pages/short_report.html', context=context)

def date_short_report(request):
    date_form = DateForm(request.GET)
    if not date_form.is_valid():
        context = {
            'enctype':'multipart/form-data',
            'method': "GET",
            'url': resolve_url('date_short_report'), 
            'form': date_form,
        }
        return render(request, 'pages/simple_form.html', context=context)
    date = date_form.cleaned_data['date']

    context = {}
    context['result_headers'] = [
        'Area', 'No. Com.', 'Pct. Com.', 'Investment', 'Investment Pct.',
        'Market Price', 'Market Price Pct.'
    ]
    sectors = {}
    locations = {}
    template = {
        'num': 0,
        'investment': 0,
        'market': 0,
    }

    # Get companies
    companies = Company.objects.filter(
        status = 1, # Portfolio status
    ).annotate(
        area = F('sector__name'),
        city = F('location__city')
    )
    total_companies = 0
    # Count companies by sector and city
    for company in companies:
        if not sectors.get(company.area):
            sectors[company.area]=template.copy()
        if not locations.get(company.city):
            locations[company.city]=template.copy()
        sectors[company.area]['num']+=1
        locations[company.city]['num']+=1
        total_companies += 1
    # Get money transactions
    money_transactions = MoneyTransaction.objects.filter(
        company__in = companies,
        portfolio__name = 'Martlet',
        date__lte = date,
    ).annotate(
        area = F('company__sector__name'),
        city = F('company__location__city'),
        type = F('transaction_type__title'),
    )
    total_money_invested = 0
    # Sum all investments
    for transaction in money_transactions:
        if transaction.type == 'Sell':
            price = -float(transaction.price)
        else:
            price = float(transaction.price)
        total_money_invested += price
        sectors[transaction.area]['investment']+=price
        locations[transaction.city]['investment']+=price
    # Get share transactions
    share_transactions = ShareTransaction.objects.filter(
        money_transaction__company__in = companies,
        date__lte = date,
    ).annotate(
        type = F('money_transaction__transaction_type__title'),
        area = F('money_transaction__company__sector__name'),
        city = F('money_transaction__company__location__city'),
    )
    total_market_price = 0
    # Sum market price
    for transaction in share_transactions:
        last_price = SharePrice.objects.last_price(share=transaction.share)
        cof = Split.objects.cof(
            date__gte = transaction.date,
            date__lte = date,
            share=transaction.share,
        )
        if transaction.type == 'Sell':
            total = -float(transaction.amount*cof*last_price)
        else:
            total = float(transaction.amount*cof*last_price)
        total_market_price += total
        sectors[transaction.area]['market']+=total
        locations[transaction.city]['market']+=total
    # Representation
    context['results_sector'] = []
    context['results_location'] = []
    context['sectors'] = []
    context['locations'] = []
    context['chart1'] = []
    context['chart2'] = []
    context['chart3'] = []
    context['chart4'] = []
    context['chart5'] = []
    context['chart6'] = []
    for key in sectors.keys():
        company_pct = 0
        investment_pct = 0
        market_price_pct = 0
        if total_companies and sectors[key]['num']:
            company_pct = 100/total_companies*sectors[key]['num']
        if total_money_invested and sectors[key]['investment']:
            investment_pct = 100/total_money_invested*sectors[key]['investment']
        if total_market_price and sectors[key]['market']:
            market_price_pct = 100/total_market_price*sectors[key]['market']
        context['results_sector'].append((
            key, sectors[key]['num'],
            round(company_pct, 1),
            int(sectors[key]['investment']),
            round(investment_pct, 1),
            int(sectors[key]['market']),
            round(market_price_pct, 1),
        ))
        context['sectors'].append(key)
        context['chart1'].append(sectors[key]['num'])
        context['chart3'].append(sectors[key]['investment'])
        context['chart5'].append(sectors[key]['market'])
    for key in locations.keys():
        company_pct = 0
        investment_pct = 0
        market_price_pct = 0
        if total_companies and locations[key]['num']:
            company_pct = 100/total_companies*locations[key]['num']
        if total_money_invested and locations[key]['investment']:
            investment_pct = 100/total_money_invested*locations[key]['investment']
        if total_market_price and locations[key]['market']:
            market_price_pct = 100/total_market_price*locations[key]['market']
        context['results_location'].append((
            key, locations[key]['num'], 
            round(company_pct, 1),
            int(locations[key]['investment']),
            round(investment_pct, 1),
            int(locations[key]['market']),
            round(market_price_pct, 1),
        ))
        context['locations'].append(key)
        context['chart2'].append(locations[key]['num'])
        context['chart4'].append(locations[key]['investment'])
        context['chart6'].append(locations[key]['market'])
    # Footer-total
    context['footer'] = [
        'Total:', total_companies, 100, int(total_money_invested),
        100, int(total_market_price), 100,
    ]
    return render(request, 'pages/short_report.html', context=context)

def upload_shareholders(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        file_type = report_file_name(file)
        initial_data = []
        special_fields = []
        company = None
        # CS01 behavior
        if file_type == "CS01":
            company_number, res, date = CS01_parser(file)
            company = Company.objects.filter(number=company_number).first()
            for index, record in enumerate(res):
                contact_type = ContactType.objects.filter(contact__name=record['owner']).first()
                if not contact_type:
                    contact_type = ContactType.objects.filter(type='No Type Info').first()
                    special_fields.append(index)
                initial_data.append({
                    'amount': record['amount'],
                    'contact_type': contact_type,
                    'type': share_name_correction(record['share']),
                    'name': record['owner']
                })
        # SH01 behavior
        elif file_type == "SH01":
            company_number, res, date = SH01_parser(file)
            company = Company.objects.filter(number=company_number).first()
            # Total share amount
            share_amounts = defaultdict(int)
            for r in res:
                share = share_name_correction(r['share'])
                share_amounts[share]+= r['amount']
            # Current shareholders
            shareholder_list = ShareholderList.objects.filter(
                company = company,
                date__lt = date,
            ).order_by('-date')[:1].first()
            shareholders = Shareholder.objects.filter(
                shareholder_list = shareholder_list
            ).annotate(
                name = F('contact__name'),
                type = F('share__type__type'),
                contact_type = F('contact__type'),
            )
            for shareholder in shareholders:
                if shareholder.option:
                    share_amounts[shareholder.type]-=shareholder.amount
                initial_data.append({
                    'amount': shareholder.amount,
                    'contact_type': shareholder.contact_type,
                    'type': shareholder.type,
                    'name': shareholder.name,
                    'option': shareholder.option,
                })
            default_contact = Contact.objects.get(pk=1) # "No Name" contact
            for key, value in share_amounts.items():
                if value<0:
                    messages.error(request, 'Liquidation error!')
                    return redirect('upload_shareholders')
                elif value>0:
                    added = False
                    # If the default_contact with the same share is
                    # already in the database, add it to it; if not, create it.
                    for record in initial_data:
                        if (record['name'] == default_contact.name and
                            record['type'] == key and
                            record['option'] == True):
                            record['amount']+=value
                            added = True
                            break
                    if not added:
                        initial_data.append({
                        'amount': value,
                        'contact_type': default_contact.type,
                        'type': key,
                        'name': default_contact.name,
                    })

        if not company:
            messages.error(request, 'Unsupported file type or non-existent company number')
            return redirect('upload_shareholders')
    
        extra_form = ShareholderListExtraForm(initial={'company':company, 'date':date})
        table_headers = initial_data[0].keys() if initial_data else []
        context = {
            'special_fields':special_fields,
            'title': company.name,
            'table_headers': table_headers,
            'formset': ShareholderUploadFormSet(initial=initial_data),
            'form_url': resolve_url('confirm_shareholders'),
            'extra_form':extra_form,
        }
        return render(request, 'pages/shareholders_formset.html', context=context)
    else:
        form = UploadFileForm()
        context = {
            'enctype':'multipart/form-data',
            'method': "POST",
            'url': resolve_url('upload_shareholders'), 
            'form': form,
        }
        return render(request, 'pages/simple_form.html', context=context)
    

def confirm_shareholders(request):
    extra_form = ShareholderListExtraForm(request.POST)
    shareholders_formset = ShareholderUploadFormSet(request.POST)
    if not shareholders_formset.is_valid() or not extra_form.is_valid():
        messages.error(request, 'Invalid form. Please try again.') 
        return redirect('upload_shareholders')
    shareholder_list, created = extra_form.get_or_create()
    if not created:
        messages.error(
            request,
            f'{extra_form.cleaned_data["company"]}|{extra_form.cleaned_data["date"]}.'\
            ' Already exists.'
        ) 
        return redirect('upload_shareholders')
    shares_before = Share.objects.filter(company=shareholder_list.company).count()
    for form in shareholders_formset:
        form.save(shareholder_list)
    shares_after = Share.objects.filter(company=shareholder_list.company).count()
    messages.success(request, 'Added successfully')
    if shares_before != shares_after:
        return redirect(
                reverse('update_prices')+'?'+
                f'company={shareholder_list.company.pk}'
            )
    return redirect('upload_shareholders')

class SharePriceUpdateView(View):
    def get(self, request):
        form = CompanySelectForm(request.GET)
        if not form.is_valid():
            context = {
                'enctype':'multipart/form-data',
                'method': "GET",
                'url': resolve_url('update_prices'), 
                'form': form,
            }
            return render(request, 'pages/simple_form.html', context=context)
        shares = Share.objects.filter(company=form.cleaned_data['company'])
        # price from GET
        price = round(float(request.GET.get('price', 0)), 8)
        # AVG company share price
        avg_price = 0
        market_value = 0
        total_shares = 0
        shareholder_list = ShareholderList.objects.filter(
            company = form.cleaned_data['company'],
        ).order_by('-date')[:1].first()
        shareholders = Shareholder.objects.filter(
            shareholder_list = shareholder_list,
            option = True,
        )
        for shareholder in shareholders:
            last_price = SharePrice.objects.last_price(
                share = shareholder.share
            )
            if last_price:
                market_value += shareholder.amount*last_price
                total_shares += shareholder.amount
        if market_value and total_shares:
            avg_price = market_value/total_shares

        initial_data = []
        for share in shares:
            last_price = SharePrice.objects.last_price(share=share)
            initial_data.append({
                'share':share,
                'price': (price or last_price or avg_price),
                'date':  request.GET['date'] if request.GET.get('date') else date.today(),
            })
        if not initial_data: 
            messages.warning(request, 'The company has no shares')
            return redirect('update_prices')

        context = {
            'title': 'Update Price',
            'formset': SharePriceFormSet(initial=initial_data),
            'form_url': resolve_url('update_prices'),
        }
        return render(request, 'pages/prices_formset.html', context=context)

    def post(self, request):
        formset = SharePriceFormSet(request.POST)
        if not formset.is_valid():
            messages.warning(request, 'Invalid form. Please try again.')
            return redirect('update_prices')
        for form in formset:
            form.save()
        return redirect('short_report')
    

class CompanyReportView(View):
    def get(self, request):
        form = CompanySelectForm(request.GET)
        if not form.is_valid():
            context = {
                'enctype':'multipart/form-data',
                'method': "GET",
                'url': resolve_url('company_report'), 
                'form': form,
            }
            return render(request, 'pages/simple_form.html', context=context)
        company = form.cleaned_data['company']
        contact = company.contact
        # Table 1
        table1 = []
        money_transactions = MoneyTransaction.objects.filter(
            company = company
        ).order_by('date')
        for money_transaction in money_transactions:
            price = money_transaction.price
            transaction_type = money_transaction.transaction_type
            portfolio = money_transaction.portfolio
            share_transactions = ShareTransaction.objects.filter(
                money_transaction = money_transaction
            ).order_by('date')
            # Calculate cost per share
            cost_per_share = 0
            total_amount = 0
            for share_transaction in share_transactions:
                total_amount += share_transaction.amount
            if total_amount:
                cost_per_share = price/total_amount

            if len(share_transactions)==0:
                table1.append([
                    money_transaction.date, price, 0, cost_per_share,
                    transaction_type, '', portfolio, money_transaction.comment,
                ])
            elif (len(share_transactions)==1 and 
                share_transactions[0].date == money_transaction.date):
                share_transaction = share_transactions[0]
                amount = share_transaction.amount
                share_type = share_transaction.share.type
                comment = f'{money_transaction.company} | {share_transaction.comment}'
                table1.append([
                    money_transaction.date, price, amount, cost_per_share,
                    transaction_type, share_type, portfolio, comment,
                ])
            else:
                table1.append([
                    money_transaction.date, price, 0, 0, transaction_type,
                    '', portfolio, money_transaction.comment
                ])
                for share_transaction in share_transactions:
                    amount = share_transaction.amount
                    share_type = share_transaction.share.type
                    table1.append([
                        share_transaction.date, 0, amount, cost_per_share,
                        '', share_type, '', share_transaction.comment
                    ])
        # Table 2
        latest_shareholder_list = ShareholderList.objects.filter(
            company = company,
        ).order_by('-date')[:1].first()
        if latest_shareholder_list:
            shareholders = Shareholder.objects.filter(
                shareholder_list = latest_shareholder_list,
            ).select_related('contact__type')
        else:
            shareholders = []

        # Percentage of company ownership
        percentage_of_ownership = 0
        our_amount = 0
        total_amount = 0
        for shareholder in shareholders:
            total_amount += shareholder.amount
        share_transactions = ShareTransaction.objects.annotate(
            portfolio = F('money_transaction__portfolio__name'),
            type = F('money_transaction__transaction_type__title'),
        ).filter(
            share__company = company
        )
        for transaction in share_transactions:
            cof = Split.objects.cof(
                date__gte = transaction.date,
                share=transaction.share,
            )
            if transaction.type == 'Sell':
                our_amount -= (
                    transaction.amount*cof
                )
            else:
                our_amount += (
                    transaction.amount*cof
                )
        if total_amount and our_amount:
            percentage_of_ownership = round(100/total_amount*our_amount, 2)

        # Price chart
        labels = []
        datasets = {}

        shares = Share.objects.filter(
            company = company,
        )
        for share in shares:
            datasets[share.type.type] = []

        share_prices = SharePrice.objects.filter(
            share__in = shares,
        ).annotate(type = F('share__type__type')).order_by('date')

        last_date = date.min
        for share_price in share_prices:
            if share_price.date == last_date:
                datasets[share_price.type][-1] = float(share_price.price)
            else:
                labels.append(str(share_price.date))
                for key, array in datasets.items():
                    if key == share_price.type:
                        array.append(float(share_price.price))
                    else:
                        if len(array):
                            array.append(array[-1])
                        else:
                            array.append(0)
            last_date = share_price.date
        
        context = {
            'table1':table1,
            'table2':shareholders,
            'company':company,
            'contact':contact,
            'percentage_of_ownership': percentage_of_ownership,
            'chart1':{
                'labels': labels,
                'datasets':datasets
            },
        }
        return render(request, 'pages/company_report.html', context)
    

class DetailedReportView(View):
    def get(self, request):
        res = {}
        context = {
            'result_headers':[
                'Company', 'Marshal Invested', 'Restructuring', 'Martlet Invested',
                'Total Amount', 'Martlet % ownership (undiluted)',
                'Martlet % ownership (fully diluted)', 'Market Price',
                'First transaction',
            ],
            'results':[],
            'links':[],
        }
        companies = Company.objects.all()
        for company in companies:
            context['links'].append(reverse('company_report')+f'?company={company.pk}')
            res[company.name] = {
                'marshal_invested': 0,
                'restructuring': 0,
                'martlet_invested': 0,
                'total_amount': 0,
                'percent_undiluted': 0,
                'percent_fully': 0,
                'market_price': 0,
                'first_transaction': 0,
            }

        money_transactions = MoneyTransaction.objects.all().annotate(
            type = F('transaction_type__title'),
            company_name = F('company__name'),
            portfolio_name = F('portfolio__name')
        )
        for transaction in money_transactions:
            value = transaction.price
            if transaction.type == 'Sell':
                value = -value
            if transaction.portfolio_name == 'Marshall':
                res[transaction.company_name]['marshal_invested'] += value
            elif transaction.portfolio_name == 'Martlet':
                res[transaction.company_name]['martlet_invested'] += value


        share_transactions = ShareTransaction.objects.annotate(
            company = F('share__company__name'),
            portfolio = F('money_transaction__portfolio__name'),
            type = F('money_transaction__transaction_type__title'),
        )
        for transaction in share_transactions:
            last_price = SharePrice.objects.last_price(share=transaction.share)
            cof = Split.objects.cof(
                date__gte = transaction.date,
                share=transaction.share,
            )
            if transaction.type == 'Sell':
                res[transaction.company]['total_amount'] -= (
                    transaction.amount*cof
                )
                res[transaction.company]['market_price'] -= float(
                    transaction.amount*cof*last_price
                )
            else:
                res[transaction.company]['total_amount'] += (
                    transaction.amount*cof
                )
                res[transaction.company]['market_price'] += float(
                    transaction.amount*cof*last_price
                )

        # Percentage of company ownership
        for key in res.keys():
            latest_shareholder_list = ShareholderList.objects.filter(
                company__name = key,
            ).order_by('-date')[:1].first()
            if latest_shareholder_list:
                our_amount = res[key]['total_amount']
                total_fully = Shareholder.objects.filter(
                    shareholder_list = latest_shareholder_list
                ).aggregate(
                    total_amount = Sum('amount')
                )['total_amount']
                total_undiluted = Shareholder.objects.filter(
                    shareholder_list = latest_shareholder_list,
                    option = True,
                ).aggregate(
                    total_amount = Sum('amount')
                )['total_amount']

                if our_amount and total_fully:
                    res[key]['percent_fully'] = round(
                        100/total_fully*our_amount, 2
                    )
                if our_amount and total_undiluted:
                    res[key]['percent_undiluted'] = round(
                        100/total_undiluted*our_amount, 2
                    )
        
        for company in companies:
                restruct = MoneyTransaction.objects.filter(
                    company = company,
                    transaction_type__title = 'Restructuring',
                ).order_by('-date')[:1].first()
                if restruct:
                    res[company.name]['restructuring'] = float(restruct.price)
                else:
                    res[company.name]['restructuring'] = 0

        for company in companies:
            first_transaction = MoneyTransaction.objects.filter(
                company = company,
            ).order_by('date')[:1].first()
            if first_transaction:
                res[company.name]['first_transaction'] = first_transaction.date 
            else:
                res[company.name]['first_transaction'] = 0

        for key, value in res.items():
            context['results'].append(
                (
                    key, value['marshal_invested'], value['restructuring'],
                    value['martlet_invested'], round(value['total_amount'], 2),
                    round(value['percent_undiluted'], 2), round(value['percent_fully'], 2),
                    round(value['market_price'], 2), value['first_transaction'],
                )
            )

        return render(request, 'pages/detailed_report.html', context=context)
        


class UpdateShareholdersView(View):
    def get(self, request):
        form = CompanySelectForm(request.GET)
        if not form.is_valid():
            context = {
                'enctype':'multipart/form-data',
                'method': "GET",
                'url': resolve_url('update_shareholders'), 
                'form': form,
            }
            return render(request, 'pages/simple_form.html', context=context)
        company = form.cleaned_data['company']
        last_shareholder_list = ShareholderList.objects.filter(
            company = company,
        ).order_by('-date')[:1].first()
        if not last_shareholder_list:
            messages.warning(request, 'The company has no shareholders')
            return redirect('update_shareholders')
        shareholders = Shareholder.objects.filter(
            shareholder_list = last_shareholder_list,
        ).annotate(
            contact_type = F('contact__type'),
            type = F('share__type__type'),
            name = F('contact__name'),
        )
        initial_data = []
        for shareholder in shareholders:
            initial_data.append({
                'amount':shareholder.amount,
                'contact_type':shareholder.contact_type,
                'type':shareholder.type,
                'name':shareholder.name,
                'option': shareholder.option,
            })
        extra_form = ShareholderListExtraForm(initial={'company':company, 'date':date.today()})
        table_headers = initial_data[0].keys() if initial_data else []
        context = {
            'title': company.name,
            'table_headers': table_headers,
            'formset': ShareholderUploadFormSet(initial=initial_data),
            'form_url': resolve_url('confirm_shareholders'),
            'extra_form':extra_form,
        }
        return render(request, 'pages/shareholders_formset.html', context=context)
    


class CurrentHoldingsView(View):
    def get(self, request):
        period_form = PeriodForm(request.GET)
        if not period_form.is_valid():
            context = {
                'enctype':'multipart/form-data',
                'method': "GET",
                'url': resolve_url('current_holdings'), 
                'form': period_form,
            }
            return render(request, 'pages/simple_form.html', context=context)
        
        reporting_date = period_form.cleaned_data['reporting']
        previous_date = period_form.cleaned_data['previous']
        # General context
        context = {
            'result_headers':[
                'Company', 'Year of investment', 'Martlet ownership',
                'Martlet direct investment cost', 'Martlet cost based on transfer value',
                f'Martlet fair value ({reporting_date})', f'Martlet fair value ({previous_date})',
                f'Valuation change {reporting_date} vs {previous_date}',
                f'New Martlet investment since {previous_date}',
                f'Valuation change {reporting_date} vs {previous_date} (excluding new Martlet investment)',
                'Fair Value Method', 'Fair value multiple to cost',
                'Fair value multiple to transfer cost',
                'Enterprise valuation as at last round',
            ],
            'table1':[],
            'table2':[],
            'links1':[],
            'links2':[],
        }
        tmp = {
            'company':'',
            'year':0,
            'ownership':0,
            'invested': 0,
            'cost': 0,
            'fair_value_rep':0,
            'fair_value_prev':0,
            'valuation_change':0,
            'new_investment':0,
            'valuation_change_exclud':0,
            'fair_value_method':'Not set',
            'fair_cost':0,
            'fair_transfer_cost':0,
            'enterprise':0,
        }
        # Table 1
        companies = Company.objects.filter(
            status = 1, # Portfolio status
            category = 1 # Companys category
        )
        res = []
        for company in companies:
            context['links1'].append(reverse('company_report')+f'?company={company.pk}')
            res.append(tmp.copy())
            # Company
            res[-1]['company'] = company.short_name
            # Year of investment
            first_investment = MoneyTransaction.objects.filter(
                company = company
            ).order_by('date')[:1].first()
            if first_investment:
                res[-1]['year'] = first_investment.date.year
            # Martlet direct investment cost
            # and
            # Martlet cost based on transfer value (including new investment)
            money_transactions = MoneyTransaction.objects.filter(
                date__lte = reporting_date,
                company = company,
            ).annotate(
                portfolio_name = F('portfolio__name'),
                type = F('transaction_type__title')
            )
            for transaction in money_transactions:
                if transaction.type == "Sell":
                    res[-1]['invested'] -= transaction.price
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price
                elif transaction.type == "Restructuring":
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price
                else:
                    res[-1]['invested'] += transaction.price
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price

            # Martlet ownership
            # and
            # Fair Value Method
            # and
            # Martlet fair value reporting_date
            reporting_shareholder_list = ShareholderList.objects.filter(
                company = company,
                date__lte = reporting_date
            ).order_by('-date')[:1].first()
            total_amount = Shareholder.objects.filter(
                shareholder_list = reporting_shareholder_list,
            ).aggregate(
                    total_amount = Sum('amount')
            )['total_amount']

            fair_value_method = FairValueMethod.objects.filter(
                company = company,
                date__lte = reporting_date, 
            ).order_by('-date')[:1].first()
            fair_value_cof = 1
            if fair_value_method:
                res[-1]['fair_value_method'] = fair_value_method.name
                fair_value_cof = Decimal(fair_value_method.percent/100)

            our_amount = 0
            price_exist = set()
            our_share_transactions = ShareTransaction.objects.filter(
                date__lte = reporting_date,
                share__company = company,
            ).annotate(
                type = F('money_transaction__transaction_type__title'),
            )
            for transaction in our_share_transactions:
                # Last price
                last_price = SharePrice.objects.filter(
                    share = transaction.share,
                    date__lte = reporting_date,
                ).order_by('-date')[:1].first()
                if last_price:
                    if last_price.date > previous_date:
                        price_exist.add(last_price.share)
                    last_price = last_price.price
                else:
                    last_price = 0
                # Split
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    date__lte = reporting_date,
                    share=transaction.share,
                )

                if transaction.type == 'Sell':
                    our_amount -= transaction.amount*cof
                    res[-1]['fair_value_rep'] -= (
                        transaction.amount*last_price*fair_value_cof*cof
                    )
                else:
                    our_amount += transaction.amount*cof
                    res[-1]['fair_value_rep'] += (
                        transaction.amount*last_price*fair_value_cof*cof
                    )
            # Add Loan to fair_value_prev
            share_money_ids = ShareTransaction.objects.filter(
                date__lte = reporting_date,
                money_transaction__company = company,
            ).values_list('money_transaction_id', flat=True)
            money_transactions = MoneyTransaction.objects.filter(
                company = company,
                date__lte = reporting_date,
                transaction_type__title = "Loan"
            ).exclude(id__in = share_money_ids)
            for transaction in money_transactions:
                res[-1]['fair_value_rep'] += transaction.price

            if total_amount and our_amount:
                res[-1]['ownership'] = our_amount/total_amount*100
            # Martlet fair value previous_date
            our_share_transactions = ShareTransaction.objects.filter(
                date__lte = previous_date,
                share__company = company,
            ).annotate(
                type = F('money_transaction__transaction_type__title'),
            )
            for transaction in our_share_transactions:
                # Last price
                last_price = SharePrice.objects.filter(
                    share = transaction.share,
                    date__lte = previous_date,
                ).order_by('-date')[:1].first()
                if last_price:
                    last_price = last_price.price
                else:
                    last_price = 0
                # Split
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    share=transaction.share,
                )

                if transaction.type == 'Sell':
                    if transaction.share in price_exist:
                        res[-1]['fair_value_prev'] -= (
                            transaction.amount*last_price*cof
                        )
                    else:
                        res[-1]['fair_value_prev'] -= (
                            transaction.amount*last_price*fair_value_cof*cof
                        )
                else:
                    if transaction.share in price_exist:
                        res[-1]['fair_value_prev'] += (
                            transaction.amount*last_price*cof
                        )
                    else:
                        res[-1]['fair_value_prev'] += (
                            transaction.amount*last_price*fair_value_cof*cof
                        )
            # Add Loan to fair_value_prev
            share_money_ids = ShareTransaction.objects.filter(
                date__lte = previous_date,
                money_transaction__company = company,
            ).values_list('money_transaction_id', flat=True)
            money_transactions = MoneyTransaction.objects.filter(
                company = company,
                date__lte = previous_date,
                transaction_type__title = "Loan",
            ).exclude(id__in = share_money_ids)
            for transaction in money_transactions:
                res[-1]['fair_value_prev'] += transaction.price

            # Valuation change reporting_date vs previous_date
            res[-1]['valuation_change'] = (
                res[-1]['fair_value_rep'] - res[-1]['fair_value_prev']
            )
            # New Martlet investment since previous_date
            money_transactions = MoneyTransaction.objects.filter(
                date__gt = previous_date,
                company = company,
                portfolio__name = 'Martlet',
            ).annotate(
                type = F('transaction_type__title')
            )
            for transaction in money_transactions:
                if transaction.type == 'Sell':
                    res[-1]['new_investment'] -= transaction.price
                else:
                    res[-1]['new_investment'] += transaction.price
            # Valuation change reporting_date vs previous_date
            res[-1]['valuation_change_exclud']=(
                res[-1]['valuation_change'] - res[-1]['new_investment']
            )
            # Fair value multiple to cost
            if res[-1]['fair_value_rep'] and res[-1]['invested']:
                res[-1]['fair_cost'] = (
                    res[-1]['fair_value_rep']/res[-1]['invested']
                )
            # Fair value multiple to transfer cost
            if res[-1]['fair_value_rep'] and res[-1]['cost']:
                res[-1]['fair_transfer_cost'] = (
                    res[-1]['fair_value_rep']/res[-1]['cost']
                )
            # Enterprise valuation (fully diluted) as at last round
            shareholder_list = ShareholderList.objects.filter(
                date__lte = reporting_date,
                company = company
            ).order_by('-date')[:1].first()
            shareholders = Shareholder.objects.filter(
                shareholder_list = shareholder_list
            )
            for shareholder in shareholders:
                last_price = SharePrice.objects.last_price(
                    share=shareholder.share,
                    date__lte = reporting_date,
                )
                res[-1]['enterprise']+=shareholder.amount*last_price

        for r in res:
            context['table1'].append((
                r['company'],
                round(r['year']),
                f"{round(r['ownership'], 2)}%",
                round(r['invested']),
                round(r['cost']),
                round(r['fair_value_rep']),
                round(r['fair_value_prev']),
                round(r['valuation_change']),
                round(r['new_investment']),
                round(r['valuation_change_exclud']),
                r['fair_value_method'],
                round(r['fair_cost'], 2),
                round(r['fair_transfer_cost'], 2),
                round(r['enterprise']),
            ))
        # Table 2
        companies = Company.objects.filter(
            status = 1, # Portfolio status
            category = 2 # Strategic category
        )
        res = []
        for company in companies:
            context['links2'].append(reverse('company_report')+f'?company={company.pk}')
            res.append(tmp.copy())
            # Company
            res[-1]['company'] = company.short_name
            # Year of investment
            first_investment = MoneyTransaction.objects.filter(
                company = company
            ).order_by('date')[:1].first()
            if first_investment:
                res[-1]['year'] = first_investment.date.year
            # Martlet direct investment cost
            # and
            # Martlet cost based on transfer value (including new investment)
            money_transactions = MoneyTransaction.objects.filter(
                date__lte = reporting_date,
                company = company,
            ).annotate(
                portfolio_name = F('portfolio__name'),
                type = F('transaction_type__title')
            )
            for transaction in money_transactions:
                if transaction.type == "Sell":
                    res[-1]['invested'] -= transaction.price
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price
                elif transaction.type == "Restructuring":
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price
                else:
                    res[-1]['invested'] += transaction.price
                    if transaction.portfolio_name == 'Martlet':
                        res[-1]['cost'] += transaction.price

            # Martlet ownership
            # and
            # Fair Value Method
            # and
            # Martlet fair value reporting_date
            reporting_shareholder_list = ShareholderList.objects.filter(
                company = company,
                date__lte = reporting_date
            ).order_by('-date')[:1].first()
            total_amount = Shareholder.objects.filter(
                shareholder_list = reporting_shareholder_list,
            ).aggregate(
                    total_amount = Sum('amount')
            )['total_amount']

            fair_value_method = FairValueMethod.objects.filter(
                company = company,
                date__lte = reporting_date, 
            ).order_by('-date')[:1].first()
            fair_value_cof = 1
            if fair_value_method:
                res[-1]['fair_value_method'] = fair_value_method.name
                fair_value_cof = Decimal(fair_value_method.percent/100)

            our_amount = 0
            price_exist = set()
            our_share_transactions = ShareTransaction.objects.filter(
                date__lte = reporting_date,
                share__company = company,
            ).annotate(
                type = F('money_transaction__transaction_type__title'),
            )
            for transaction in our_share_transactions:
                # Last price
                last_price = SharePrice.objects.filter(
                    share = transaction.share,
                    date__lte = reporting_date,
                ).order_by('-date')[:1].first()
                if last_price:
                    if last_price.date > previous_date:
                        price_exist.add(last_price.share)
                    last_price = last_price.price
                else:
                    last_price = 0
                # Split
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    date__lte = reporting_date,
                    share=transaction.share,
                )

                if transaction.type == 'Sell':
                    our_amount -= transaction.amount*cof
                    res[-1]['fair_value_rep'] -= (
                        transaction.amount*last_price*fair_value_cof*cof
                    )
                else:
                    our_amount += transaction.amount*cof
                    res[-1]['fair_value_rep'] += (
                        transaction.amount*last_price*fair_value_cof*cof
                    )
            # Add Loan to fair_value_prev
            share_money_ids = ShareTransaction.objects.filter(
                date__lte = reporting_date,
                money_transaction__company = company,
            ).values_list('money_transaction_id', flat=True)
            money_transactions = MoneyTransaction.objects.filter(
                company = company,
                date__lte = reporting_date,
                transaction_type__title = "Loan"
            ).exclude(id__in = share_money_ids)
            for transaction in money_transactions:
                res[-1]['fair_value_rep'] += transaction.price

            if total_amount and our_amount:
                res[-1]['ownership'] = our_amount/total_amount*100
            # Martlet fair value previous_date
            our_share_transactions = ShareTransaction.objects.filter(
                date__lte = previous_date,
                share__company = company,
            ).annotate(
                type = F('money_transaction__transaction_type__title'),
            )
            for transaction in our_share_transactions:
                # Last price
                last_price = SharePrice.objects.filter(
                    share = transaction.share,
                    date__lte = previous_date,
                ).order_by('-date')[:1].first()
                if last_price:
                    last_price = last_price.price
                else:
                    last_price = 0
                # Split
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    share=transaction.share,
                )

                if transaction.type == 'Sell':
                    if transaction.share in price_exist:
                        res[-1]['fair_value_prev'] -= (
                            transaction.amount*last_price*cof
                        )
                    else:
                        res[-1]['fair_value_prev'] -= (
                            transaction.amount*last_price*fair_value_cof*cof
                        )
                else:
                    if transaction.share in price_exist:
                        res[-1]['fair_value_prev'] += (
                            transaction.amount*last_price*cof
                        )
                    else:
                        res[-1]['fair_value_prev'] += (
                            transaction.amount*last_price*fair_value_cof*cof
                        )
            # Add Loan to fair_value_prev
            share_money_ids = ShareTransaction.objects.filter(
                date__lte = previous_date,
                money_transaction__company = company,
            ).values_list('money_transaction_id', flat=True)
            money_transactions = MoneyTransaction.objects.filter(
                company = company,
                date__lte = previous_date,
                transaction_type__title = "Loan",
            ).exclude(id__in = share_money_ids)
            for transaction in money_transactions:
                res[-1]['fair_value_prev'] += transaction.price

            # Valuation change reporting_date vs previous_date
            res[-1]['valuation_change'] = (
                res[-1]['fair_value_rep'] - res[-1]['fair_value_prev']
            )
            # New Martlet investment since previous_date
            money_transactions = MoneyTransaction.objects.filter(
                date__gt = previous_date,
                company = company,
                portfolio__name = 'Martlet',
            ).annotate(
                type = F('transaction_type__title')
            )
            for transaction in money_transactions:
                if transaction.type == 'Sell':
                    res[-1]['new_investment'] -= transaction.price
                else:
                    res[-1]['new_investment'] += transaction.price
            # Valuation change reporting_date vs previous_date
            res[-1]['valuation_change_exclud']=(
                res[-1]['valuation_change'] - res[-1]['new_investment']
            )
            # Fair value multiple to cost
            if res[-1]['fair_value_rep'] and res[-1]['invested']:
                res[-1]['fair_cost'] = (
                    res[-1]['fair_value_rep']/res[-1]['invested']
                )
            # Fair value multiple to transfer cost
            if res[-1]['fair_value_rep'] and res[-1]['cost']:
                res[-1]['fair_transfer_cost'] = (
                    res[-1]['fair_value_rep']/res[-1]['cost']
                )
            # Enterprise valuation (fully diluted) as at last round
            shareholder_list = ShareholderList.objects.filter(
                date__lte = reporting_date,
                company = company
            ).order_by('-date')[:1].first()
            shareholders = Shareholder.objects.filter(
                shareholder_list = shareholder_list
            )
            for shareholder in shareholders:
                last_price = SharePrice.objects.last_price(
                    share=shareholder.share,
                    date__lte = reporting_date,
                )
                res[-1]['enterprise']+=shareholder.amount*last_price

        for r in res:
            context['table2'].append((
                r['company'],
                round(r['year']),
                f"{round(r['ownership'], 2)}%",
                round(r['invested']),
                round(r['cost']),
                round(r['fair_value_rep']),
                round(r['fair_value_prev']),
                round(r['valuation_change']),
                round(r['new_investment']),
                round(r['valuation_change_exclud']),
                r['fair_value_method'],
                round(r['fair_cost'], 2),
                round(r['fair_transfer_cost'], 2),
                round(r['enterprise']),
            ))
        return render(request, 'pages/current_holdings.html', context=context)
    

class SharesInfoView(View):
    def get(self, request):
        date_form = DateForm(request.GET)
        if not date_form.is_valid():
            context = {
                'enctype':'multipart/form-data',
                'method': "GET",
                'url': resolve_url('shares_info'), 
                'form': date_form,
            }
            return render(request, 'pages/simple_form.html', context=context)
        reporting_date = date_form.cleaned_data['date']
        context = {
            'result_headers':[
                'Company', 'Enterprise (undiluted) as at last round',
                'Enterprise (fully diluted) as at last round',
                'Share price at last round', 'Martlet shares',
                'Total number of shares issued', 'Option pool',
                'Option pool size', 'Martlet % ownership (undiluted)',
                'Martlet % ownership (fully diluted)',
            ],
            'results':[],
            'links':[],
        }
        tmp = {
            'company':'',
            'enterprise_undiluted':0,
            'enterprise_fully':0,
            'share_price':0,
            'our_shares':0,
            'total_shares':0,
            'option_pool':0,
            'option_size':0,
            'ownership_undiluted':0,
            'ownership_fully':0,
        }
        res = []
        companies = Company.objects.filter(
            status = 1, # Portfolio status
        )
        for company in companies:
            res.append(tmp.copy())
            context['links'].append(reverse('company_report')+f'?company={company.pk}')
            # Company
            res[-1]['company']=company.name
            # Enterprise valuation (undiluted)
            # and
            # Enterprise valuation (fully)
            # and
            # Total number of shares issued
            # and
            # Option pool
            shareholder_list = ShareholderList.objects.filter(
                company = company,
                date__lte = reporting_date,
            ).order_by('-date')[:1].first()
            shareholders = Shareholder.objects.filter(
                shareholder_list=shareholder_list
            )
            for shareholder in shareholders:
                last_price = SharePrice.objects.last_price(
                    date__lte = reporting_date,
                    share = shareholder.share, 
                )
                if shareholder.option:
                    res[-1]['total_shares']+=shareholder.amount
                    res[-1]['enterprise_undiluted']+= (
                        shareholder.amount * last_price
                    )
                else:
                    res[-1]['option_pool']+=shareholder.amount
                res[-1]['enterprise_fully'] += (
                    shareholder.amount * last_price
                )
            # Martlet shares
            share_transactions = ShareTransaction.objects.filter(
                share__company = company,
                date__lte = reporting_date,
            )
            for transaction in share_transactions:
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    date__lte = reporting_date,
                    share = transaction.share,
                )
                res[-1]['our_shares'] += (
                    transaction.amount*cof
                )
            # Share price at last round
            # and
            # Option pool size
            if res[-1]['total_shares'] or res[-1]['option_pool']:
                res[-1]['share_price'] = (
                    res[-1]['enterprise_fully']/(res[-1]['total_shares']+res[-1]['option_pool'])
                )
                res[-1]['option_size'] = (
                    res[-1]['option_pool']/(res[-1]['option_pool']+res[-1]['total_shares'])*100
                )
            # Martlet ownership (undiluted)
            # and
            # Martlet ownership (fully)
            if res[-1]['our_shares'] and res[-1]['total_shares']:
                res[-1]['ownership_undiluted'] = (
                    res[-1]['our_shares']/res[-1]['total_shares']*100
                )
                res[-1]['ownership_fully'] = (
                    res[-1]['our_shares']/(res[-1]['total_shares']+res[-1]['option_pool'])*100
                )
                
        
        for r  in res:
            context['results'].append((
                r['company'],
                round(r['enterprise_undiluted']),
                round(r['enterprise_fully']),
                round(r['share_price'], 2),
                round(r['our_shares']),
                round(r['total_shares']),
                round(r['option_pool']),
                f"{round(r['option_size'], 2)}%",
                f"{round(r['ownership_undiluted'], 2)}%",
                f"{round(r['ownership_fully'], 2)}%",
            ))
        return render(request, 'pages/shares_info.html', context=context)

class SharesControlView(View):
    def get(self, request):
        context = {'extra_form': DateForm()}
        initail_data = []
        for company in Company.objects.all():
            initail_data.append({'company': company.pk})
        context['formset'] = SharesControlFormSet(initial=initail_data)
        return render(request, 'pages/shares_control.html', context=context)
    
    def post(self, request):
        date_form = DateForm(request.POST)
        control_formset = SharesControlFormSet(request.POST)
        if not control_formset.is_valid() or not date_form.is_valid():
            messages.error(request, 'Invalid Form')
            return redirect('shares_control')
        # Errors check
        res = []
        for form in control_formset:
            if not form.cleaned_data['shares'] and not form.cleaned_data['options']:
                continue
            shareholders = form.create(date_form.cleaned_data['date'])
            if shareholders is None:
                messages.error(request, f'Liquidation or already exists: {form.cleaned_data["company"]}')
                context = {'extra_form': date_form, 'formset':control_formset}
                return render(request, 'pages/shares_control.html', context=context)
            res.extend(shareholders)
        # Final save
        for obj in res:
            obj.shareholder_list.save()
            obj.save()

        messages.success(request, 'Added successfully')
        return redirect('shares_control')
        

class QuarterGraphslView(View):
    def get(self, request):
        labels = []
        market_prices = []
        investments = []
        # Report for N quarters in reverse order
        N = 8
        for date_gte, date_lt in previous_quarters(N):
            labels.append(get_fiscal_quarter(date_gte))
            
            share_transactions = ShareTransaction.objects.filter(
                date__lt = date_lt,
            ).annotate(
                    type = F('money_transaction__transaction_type__title'),
            )
            total_market_price = 0
            # Sum market price
            for transaction in share_transactions:
                last_price = SharePrice.objects.last_price(share=transaction.share)
                cof = Split.objects.cof(
                    date__gte = transaction.date,
                    date__lt = date_lt,
                    share=transaction.share,
                )
                if transaction.type == 'Sell':
                    total = -float(transaction.amount*cof*last_price)
                else:
                    total = float(transaction.amount*cof*last_price)
                total_market_price += total

            # Get money transactions
            money_transactions = MoneyTransaction.objects.filter(
                portfolio__name = 'Martlet',
                date__gte = date_gte,
                date__lt = date_lt
            ).annotate(
                type = F('transaction_type__title'),
            )
            total_invested = 0
            # Sum all investments
            for transaction in money_transactions:
                if transaction.type == 'Sell':
                    price = -float(transaction.price)
                else:
                    price = float(transaction.price)
                total_invested += price
            market_prices.append(int(total_market_price))
            investments.append(int(total_invested))
        # Changing the order
        labels = labels[::-1]
        market_prices = market_prices[::-1]
        investments = investments[::-1]
        
        # Calculate growth
        # First record have no growth
        growths = [0]
        previous_months = [market_prices[0]]
        for index in range(1, len(market_prices)):
            prev_value = previous_months[index-1]
            prev_growth = growths[index-1]
            growth = market_prices[index]-(prev_value+prev_growth)
            growths.append(growth)
            previous_months.append(prev_value+prev_growth)

        context = {
            'labels':labels,
            'investments':investments,
            'growths':growths,
            'previous_months':previous_months,
        }
        return render(request, 'pages/quarter_report.html', context)
    


class CategoryPerformanceView(View):
    def brake_into_categories(self, records:list):
        # Category boundaries
        GOLD_MAX=float('inf')
        GOLD_MIN = 500_000
        SILVER_MAX = 500_000
        SILVER_MIN = 100_000
        BRONZE_MAX = 100_000
        BRONZE_MIN = 0
        
        gold = []
        silver = []
        bronze = []

        for record in records:
            val = record['fair_value']
            if BRONZE_MIN <= val < BRONZE_MAX:
                bronze.append(record)
            elif SILVER_MIN <= val < SILVER_MAX:
                silver.append(record)
            elif GOLD_MIN <= val < GOLD_MAX:
                gold.append(record)
        
        return gold, silver, bronze


    def build_record(self, company:Company):
        res = {
            'name':'',
            'sector':'',
            'first_investment':0,
            'shareholding_pct': 0,
            'fair_value':0,
            'cost':0,
            'multiple_times':0,
        }
        # Name
        res['name'] = company.short_name
        # Sector
        res['sector'] = company.sector.short_name
        # First investment date
        first_investment = MoneyTransaction.objects.filter(
            company=company,
        ).order_by('date')[:1].first()
        if first_investment:
            res['first_investment'] = first_investment.date.year
        # Shareholding percent
        last_share_amount = 0
        our_share_amount = 0
        last_shareholder_list = ShareholderList.objects.filter(
            company=company,
        ).order_by('-date')[:1].first()
        if last_shareholder_list:
            last_share_amount = Shareholder.objects.filter(
                shareholder_list = last_shareholder_list,
            ).aggregate(total=Sum('amount'))['total']
        our_share_transactions = ShareTransaction.objects.filter(
            money_transaction__company=company,
        ).select_related(
            'share',
        ).annotate(type=F('money_transaction__transaction_type__title'))
        for transaction in our_share_transactions:
            if transaction.type == 'Sell':
                our_share_amount -= transaction.amount
            else:
                our_share_amount += transaction.amount
        if last_share_amount:
            res['shareholding_pct'] = 100/last_share_amount*our_share_amount
        # Martlet fair value
        for transaction in our_share_transactions:
            last_price = SharePrice.objects.last_price(share=transaction.share)
            cof = Split.objects.cof(
                date__gte = transaction.date,
                share=transaction.share,
            )
            if transaction.type == 'Sell':
                res['fair_value'] -= (transaction.amount*cof*last_price)
            else:
                res['fair_value'] += (transaction.amount*cof*last_price)
        # Add Loan to fair_value_prev
        share_money_ids = ShareTransaction.objects.filter(
            money_transaction__company = company,
        ).values_list('money_transaction_id', flat=True)
        money_transactions = MoneyTransaction.objects.filter(
            company = company,
            transaction_type__title = "Loan"
        ).exclude(id__in = share_money_ids)
        for transaction in money_transactions:
            res['fair_value'] += transaction.price
        # Martlet cost
        martlet_money_transactions = MoneyTransaction.objects.filter(
            company=company,
            portfolio__name = 'Martlet',
        ).annotate(type=F('transaction_type__title'))
        for transaction in martlet_money_transactions:
            if transaction.type == 'Sell':
                res['cost'] -= transaction.price
            else:
                res['cost'] += transaction.price
        # Multiple times 
        if res['cost']:
            res['multiple_times'] = res['fair_value']/res['cost']
        
        return res
    
    def add_percent_columns(self, records:list):
        total_fair_value = 0
        total_cost = 0
        for record in records:
            total_fair_value += record['fair_value']
            total_cost += record['cost']
        
        for record in records:
            record['fair_value_pct'] = 0
            record['cost_pct'] = 0
            if total_fair_value:
                record['fair_value_pct'] = 100/total_fair_value*record['fair_value']
            if total_cost:
                record['cost_pct'] = 100/total_cost*record['cost']        
        return records
    
    def format_records(self, records):
        for record in records:
            record['shareholding_pct'] = round(record['shareholding_pct'], 2)
            record['fair_value'] = int(record['fair_value'])
            record['fair_value_pct'] = round(record['fair_value_pct'], 2)
            record['cost'] = int(record['cost'])
            record['cost_pct'] = round(record['cost_pct'], 2)
            record['multiple_times'] = round(record['multiple_times'], 2)
        return records

    def get(self, request):
        headers = [
            'Company', 'Sector', 'Year of first investment', 'Shareholding',
            'Martlet fair value', 'Percent of Total Portfolio', 'Martlet cost',
            'Percent of Total Portfolio', 'Multiple Times'
        ]
        companies = Company.objects.all().select_related(
            'sector'
        )
        records = []
        for company in companies:
            records.append(self.build_record(company))
        records = self.add_percent_columns(records)
        records = self.format_records(records)
        gold, silver, bronze = self.brake_into_categories(records)
        context = {
            'result_headers':headers,
            'gold':gold,
            'silver':silver,
            'bronze':bronze,
        }
        return render(request, 'pages/category_performance.html', context)
        




