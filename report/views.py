from datetime import date

from django.contrib import messages
from django.views.generic import View
from django.urls import reverse
from django.shortcuts import render, resolve_url, redirect
from django.db.models import (
    F, OuterRef, Subquery, Sum,
)

from core.settings import PORTFOLIO
from utils.pdf_utils import shareholders_from_pdf
from home.models import (
    Company, ContactType, Share, MoneyTransaction, ShareTransaction,
    SharePrice, Split, ShareholderList, Shareholder, FairValueMethod,
)
from .forms import (
    UploadFileForm, ShareholderListExtraForm, CompanySelectForm,
    ShareholderUploadFormSet, SharePriceFormSet, PeriodForm,
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
        portfolio__name = PORTFOLIO,
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
        last_price = SharePrice.objects.filter(share=transaction.share).order_by('-date')[:1]
        splits = Split.objects.filter(
            date__gte = transaction.date,
            share=transaction.share,
        ).annotate(
            cof = F('after')/F('before'),
        ).values_list('cof')
        cof = 1
        for split in splits:
            cof *= split[0]
        if last_price.exists():
            last_price = last_price.first().price
        else:
            last_price = 0
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
        context['results_sector'].append((
            key, sectors[key]['num'],
            round(100/total_companies*sectors[key]['num'], 1),
            sectors[key]['investment'],
            round(100/total_money_invested*sectors[key]['investment'], 1),
            round(sectors[key]['market'], 2),
            round(100/total_market_price*sectors[key]['market'], 1),
        ))
        context['sectors'].append(key)
        context['chart1'].append(sectors[key]['num'])
        context['chart3'].append(sectors[key]['investment'])
        context['chart5'].append(sectors[key]['market'])
    for key in locations.keys():
        context['results_location'].append((
            key, locations[key]['num'], 
            round(100/total_companies*locations[key]['num'], 1),
            locations[key]['investment'],
            round(100/total_money_invested*locations[key]['investment'], 1),
            round(locations[key]['market'], 2),
            round(100/total_market_price*locations[key]['market'], 1),
        ))
        context['locations'].append(key)
        context['chart2'].append(locations[key]['num'])
        context['chart4'].append(locations[key]['investment'])
        context['chart6'].append(locations[key]['market'])
    # Footer-total
    context['footer'] = [
        'Total:', total_companies, 100, round(total_money_invested, 2),
        100, round(total_market_price, 2), 100,
    ]
    return render(request, 'pages/short_report.html', context=context)

def upload_shareholders(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        company, shareholders = shareholders_from_pdf(file)
        company = Company.objects.filter(name=company).first()
        if not company or not shareholders:
            messages.error(request, 'Unsupported file type or non-existent company')
            return redirect('upload_shareholders')
        initial_data = []
        special_fields = []
        for ind in range(len(shareholders)):
            contact_type = ContactType.objects.filter(contact__name=shareholders[ind][2]).first()
            blank_type = ContactType.objects.filter(type='No Type Info').first()
            if not contact_type: special_fields.append(ind)
            initial_data.append({
                'amount':shareholders[ind][0],
                'contact_type':contact_type if contact_type else blank_type,
                'type':shareholders[ind][1],
                'name':shareholders[ind][2],
            })
        extra_form = ShareholderListExtraForm(initial={'company':company, 'date':date.today()})
        table_headers = initial_data[0].keys() if initial_data else []
        context = {
            'special_fields':special_fields,
            'title': company.name,
            'table_headers': table_headers,
            'formset': ShareholderUploadFormSet(initial=initial_data),
            'form_url': resolve_url('confirm_shareholders'),
            'extra_form':extra_form,
        }
        return render(request, 'pages/table_formset.html', context=context)
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
    shareholders_set_form = ShareholderUploadFormSet(request.POST)
    if not shareholders_set_form.is_valid() or not extra_form.is_valid():
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
    for form in shareholders_set_form:
        form.save(shareholder_list)
    messages.success(request, 'Added successfully.')
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
        initial_data = []
        for share in shares:
            initial_data.append({
                'share':share,
                'price': round(float(request.GET.get('price', 0)), 3),
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
        return render(request, 'pages/table_formset.html', context=context)

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
            splits = Split.objects.filter(
                date__gte = transaction.date,
                share=transaction.share,
            ).annotate(
                cof = F('after')/F('before'),
            ).values_list('cof')
            cof = 1
            for split in splits:
                cof *= split[0]
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
            'results':shareholders,
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
            last_price = SharePrice.objects.filter(share=transaction.share).order_by('-date')[:1]
            splits = Split.objects.filter(
                date__gte = transaction.date,
                share=transaction.share,
            ).annotate(
                cof = F('after')/F('before'),
            ).values_list('cof')
            cof = 1
            for split in splits:
                cof *= split[0]
            if last_price.exists():
                last_price = last_price.first().price
            else:
                last_price = 0
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
        return render(request, 'pages/table_formset.html', context=context)
    


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
            'results':[],
            'links':[],
        }
        companies = Company.objects.filter(
            status = 1, # Portfolio status
        )
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
        res = []
        for company in companies:
            context['links'].append(reverse('company_report')+f'?company={company.pk}')
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
                fair_value_cof = fair_value_method.percent/100

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
                splits = Split.objects.filter(
                    date__gte = transaction.date,
                    share=transaction.share,
                ).annotate(
                    cof = F('after')/F('before'),
                ).values_list('cof')
                cof = 1
                for split in splits:
                    cof *= split[0]

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
                splits = Split.objects.filter(
                    date__gte = transaction.date,
                    share=transaction.share,
                ).annotate(
                    cof = F('after')/F('before'),
                ).values_list('cof')
                cof = 1
                for split in splits:
                    cof *= split[0]

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
                pass
                last_price = SharePrice.objects.filter(
                    share=shareholder.share,
                    date__lte = reporting_date,
                ).order_by('-date')[:1].first()
                if last_price:
                    last_price = last_price.price
                else:
                    last_price = 0
                res[-1]['enterprise']+=shareholder.amount*last_price

        for r in res:
            context['results'].append((
                r['company'],
                int(r['year']),
                f"{round(r['ownership'], 2)}%",
                int(r['invested']),
                int(r['cost']),
                int(r['fair_value_rep']),
                int(r['fair_value_prev']),
                int(r['valuation_change']),
                int(r['new_investment']),
                int(r['valuation_change_exclud']),
                r['fair_value_method'],
                round(r['fair_cost'], 2),
                round(r['fair_transfer_cost'], 2),
                int(r['enterprise']),
            ))
        return render(request, 'pages/current_holdings.html', context=context)