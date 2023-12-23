from django.urls import path, include

from . import views


urlpatterns = [
    path('report/short/', views.report_short, name='report_short'),
    path('report/company/', views.CompanyReportView.as_view(), name='company_report'),
    path('utils/upload/', views.upload_shareholders, name='upload_shareholders'),
    path('utils/confirm/', views.confirm_shareholders, name='confirm_shareholders'),
    path('utils/updateprices/', views.SharePriceUpdateView.as_view(), name='update_prices')
]
