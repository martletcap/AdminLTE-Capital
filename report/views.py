from django.shortcuts import render
from django.db.models import Sum, F, OuterRef, Subquery, DecimalField

from home.models import OurTransaction, SharePrice

# Create your views here.

def report_short(request):
    latest_price = SharePrice.objects.filter(
        share=OuterRef('share_id')
    ).order_by('-date')

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
    sectors = []
    parts = []
    for sector in query:
        if sector['total_sum'] is not None:
            sectors.append(sector['sector'])
            parts.append(int(sector['total_sum']))

    context = {
        'name':'Pie Chart',
        'names': sectors,
        'values': parts,
    }
    # Page from the theme 
    return render(request, 'pages/report_short.html', context=context)