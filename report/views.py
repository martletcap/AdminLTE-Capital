from django.shortcuts import render, get_object_or_404
from django.forms import formset_factory
from django.db.models import Sum, F, OuterRef, Subquery, DecimalField, Count

from utils.pdf_utils import shareholders_from_pdf
from home.models import OurTransaction, SharePrice, Company
from .forms import UploadFileForm, ShareholderUploadForm


def chart_context(title:str, query, field1:str, field2:str)->dict:
    titles = []
    values = []
    for record in query:
        if record[field2] is not None:
            titles.append(record[field1])
            values.append(int(record[field2]))
    return {'title':title, 'titles':titles, 'values':values}

# Create your views here.
def report_short(request):
    context = dict()

    # Helper subquery
    latest_price = SharePrice.objects.filter(
        share=OuterRef('share_id')
    ).order_by('-date')

    # Chart 1
    query = Company.objects.filter(
        status__status = 'Portfolio',
    ).values(
        sector_name=F('sector__name')
    ).annotate(
        total_count = Count('id')
    )
        
    context['chart1'] = chart_context(
        'No. Cos. Sector', query, 'sector_name', 'total_count',
    )

    # Chart 2
    query = Company.objects.filter(
        status__status = 'Portfolio',
    ).values(
        location_city=F('location__city')
    ).annotate(
        total_count = Count('id')
    )
        
    context['chart2'] = chart_context(
        'No. Cos. City', query, 'location_city', 'total_count',
    )

    # Chart 3
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).annotate(
        total = F('amount')*F('price')
    ).values(
        sector_name=F('share__company__sector__name')
    ).annotate(
        total_sum = Sum('total')
    )
    context['chart3'] = chart_context(
        'Investment Sector', query, 'sector_name', 'total_sum',
    )

    # Chart 4
    query = OurTransaction.objects.filter(
        share__company__status__status = 'Portfolio',
    ).annotate(
        total = F('amount')*F('price')
    ).values(
        location_city=F('share__company__location__city')
    ).annotate(
        total_sum = Sum('total')
    )
    context['chart4'] = chart_context(
        'Investment City', query, 'location_city', 'total_sum',
    )

    # Chart 5
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
        sector_name=F('share__company__sector__name')
    ).annotate(
        total_sum = Sum('total')
    )
    context['chart5'] = chart_context(
        'Market Price Sector', query, 'sector_name', 'total_sum',
    )

    # Chart 6
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
        location_city=F('share__company__location__city')
    ).annotate(
        total_sum = Sum('total')
    )
    context['chart6'] = chart_context(
        'Market Price City', query, 'location_city', 'total_sum',
    )
    

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
    


    # # Chart 3
    # query = OurTransaction.objects.filter(
    #     share__company__status__status = 'Portfolio',
    # ).annotate(
    #     last_price=Subquery(
    #         latest_price.values('price')[:1],
    #         output_field=DecimalField()
    #     )
    # ).annotate(
    #     total = F('amount')*F('last_price')
    # ).values(
    #     sector=F('share__company__sector__name')
    # ).annotate(
    #     total_sum = Sum('total')
    # )
    # titles3 = []
    # values3 = []
    # for sector in query:
    #     if sector['total_sum'] is not None:
    #         titles3.append(sector['sector'])
    #         values3.append(int(sector['total_sum']))
    # context['chart3'] = {'name':'Investment Sector', 'titles':titles3, 'values':values3}

    # # Chart 4
    # query = OurTransaction.objects.filter(
    #     share__company__status__status = 'Portfolio',
    # ).annotate(
    #     last_price=Subquery(
    #         latest_price.values('price')[:1],
    #         output_field=DecimalField()
    #     )
    # ).annotate(
    #     total = F('amount')*F('last_price')
    # ).values(
    #     location=F('share__company__location__city')
    # ).annotate(
    #     total_sum = Sum('total')
    # )
    # titles4 = []
    # values4 = []
    # for sector in query:
    #     if sector['total_sum'] is not None:
    #         titles4.append(sector['location'])
    #         values4.append(int(sector['total_sum']))
    # context['chart4'] = {'name':'Investment City', 'titles':titles4, 'values':values4}