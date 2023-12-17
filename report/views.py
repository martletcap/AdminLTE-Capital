from django.shortcuts import render, get_object_or_404
from django.forms import formset_factory
from django.db.models import Sum, F, OuterRef, Subquery, DecimalField

from utils.pdf_utils import shareholders_from_pdf
from home.models import OurTransaction, SharePrice, Company, Shareholder
from .forms import UploadFileForm, ShareholderUploadForm

# Create your views here.

def report_short(request):
    context = dict()

    latest_price = SharePrice.objects.filter(
        share=OuterRef('share_id')
    ).order_by('-date')

    # Chart 1
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).annotate(
        last_price=Subquery(
            latest_price.values('price')[:1],
            output_field=DecimalField()
        )
    ).annotate(
        total = F('amount')*F('last_price')
    ).values(
        sector=F('share__company__sector__name')
    ).annotate(
        total_sum = Sum('total')
    )
    titles1 = []
    values1 = []
    for sector in query:
        if sector['total_sum'] is not None:
            titles1.append(sector['sector'])
            values1.append(int(sector['total_sum']))
    context['chart1'] = {'name':'Pie Chart Price', 'titles':titles1, 'values':values1}

    # Chart 2
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).values(
        sector=F('share__company__sector__name')
    ).annotate(
        total_sum = Sum('amount')
    )
    titles2 = []
    values2 = []
    for sector in query:
        titles2.append(sector['sector'])
        values2.append(sector['total_sum'])
    context['chart2'] = {'name':'Pie Chart Amount', 'titles':titles2, 'values':values2}

    # Chart 3
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).annotate(
        last_price=Subquery(
            latest_price.values('price')[:1],
            output_field=DecimalField()
        )
    ).annotate(
        total = F('amount')*F('last_price')
    ).values(
        location=F('share__company__location__city')
    ).annotate(
        total_sum = Sum('total')
    )
    titles3 = []
    values3 = []
    for sector in query:
        if sector['total_sum'] is not None:
            titles3.append(sector['location'])
            values3.append(int(sector['total_sum']))
    context['chart3'] = {'name':'Pie Chart Price', 'titles':titles3, 'values':values3}

    # Chart 4
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).values(
        location=F('share__company__location__city')
    ).annotate(
        total_sum = Sum('amount')
    )
    titles4 = []
    values4 = []
    for sector in query:
        titles4.append(sector['location'])
        values4.append(sector['total_sum'])
    context['chart4'] = {'name':'Pie Chart Amount', 'titles':titles4, 'values':values4}

    # Page from the theme 
    return render(request, 'pages/report_short.html', context=context)


def upload_shareholders(request):
    if request.method == "POST":
        company, shareholders = shareholders_from_pdf(request.FILES.get('file'))
        ShareholderFormset = formset_factory(ShareholderUploadForm)
        company = get_object_or_404(Company, name=company)
        initial_data = []
        for share in shareholders:
            initial_data.append({
                'amount':share[0],
                'type':share[1],
                'name':share[2],
                'company':company,
            })
        context = {
            'formset': ShareholderFormset(initial=initial_data),
        }
        return render(request, 'pages/shareholders_chek.html', context=context)
    else:
        form = UploadFileForm()
        context = {
            'form': form
        }
        return render(request, 'pages/file_upload_form.html', context=context)
    