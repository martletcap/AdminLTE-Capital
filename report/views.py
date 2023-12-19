from decimal import Decimal

from django.contrib import messages
from django.shortcuts import render, resolve_url, redirect
from django.forms import formset_factory
from django.db.models import Sum, F, OuterRef, Subquery, DecimalField, Count

from utils.pdf_utils import shareholders_from_pdf
from home.models import OurTransaction, SharePrice, Company, Sector, Location
from .forms import UploadFileForm, ShareholderUploadForm


def none_to_zero(array:list):
    new_array = []
    for record in array:
        new_array.append([])
        for ind in range(len(record)):
            if record[ind] is None:
                new_array[-1].append(0)
            elif isinstance(record[ind], Decimal):
                new_array[-1].append(int(record[ind]))
            else:
                new_array[-1].append(record[ind])
    return new_array


# Create your views here.
def report_short(request):
    context = dict()
    context['result_headers'] = [
        'Area', 'No. Cos.', 'Investment', 'Market Price',
    ]

    latest_price = SharePrice.objects.filter(
        share_id=OuterRef('company__share__ourtransaction__share_id')
    ).order_by('-date').values('price')[:1]

    # Sector data
    res = Sector.objects.filter(
        company__status__status='Portfolio',
    ).annotate(
        num_companies=Count('company', distinct=True),
        purchase_amount=Sum(
            F('company__share__ourtransaction__amount')*
            F('company__share__ourtransaction__price')
        ),
        market_value = Sum(
            F('company__share__ourtransaction__amount')*
            Subquery(latest_price)
        )
    ).values_list('name', 'num_companies', 'purchase_amount', 'market_value')
    context['results_sector'] = none_to_zero(res)


    # Location data
    res = Location.objects.annotate(
        num_companies=Count('company', distinct=True),
        purchase_amount=Sum(
            F('company__share__ourtransaction__amount')*
            F('company__share__ourtransaction__price')
        ),
        market_value = Sum(
            F('company__share__ourtransaction__amount')*
            Subquery(latest_price)
        )
    ).values_list('city', 'num_companies', 'purchase_amount', 'market_value')
    context['results_location'] = none_to_zero(res)

    # Chart data
    context['sectors'] = []
    context['locations'] = []
    context['chart1'] = []
    context['chart2'] = []
    context['chart3'] = []
    context['chart4'] = []
    context['chart5'] = []
    context['chart6'] = []
    for record in context['results_sector']:
        context['sectors'].append(record[0])
        context['chart1'].append(record[1])
        context['chart3'].append(record[2])
        context['chart5'].append(record[3])
    for record in context['results_location']:
        context['locations'].append(record[0])
        context['chart2'].append(record[1])
        context['chart4'].append(record[2])
        context['chart6'].append(record[3])
    
    # Page from the theme 
    return render(request, 'pages/report_short.html', context=context)


def upload_shareholders(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        company, shareholders = shareholders_from_pdf(file)
        ShareholderFormset = formset_factory(ShareholderUploadForm)
        company = Company.objects.filter(name=company).first()
        if not company or not shareholders:
            messages.error(request, 'Unsupported file type or non-existent company')
            form = UploadFileForm()
            return render(request, 'pages/file_upload_form.html', context={'form': form})
        initial_data = []
        for share in shareholders:
            initial_data.append({
                'amount':share[0],
                'type':share[1],
                'name':share[2],
                'company':company.pk,
            })
        context = {
            'title': company.name,
            'formset': ShareholderFormset(initial=initial_data),
            'form_url': resolve_url('confirm_shareholders')
        }
        return render(request, 'pages/shareholders_chek.html', context=context)
    else:
        form = UploadFileForm()
        context = {'form': form}
        return render(request, 'pages/file_upload_form.html', context=context)
    

def confirm_shareholders(request):
    return redirect('index')