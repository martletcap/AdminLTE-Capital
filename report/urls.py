from django.urls import path, include

from . import views


urlpatterns = [
    # path('report/short/', views.short_report, name='short_report'),
    # path('report/company/', views.CompanyReportView.as_view(), name='company_report'),
    # path('report/detailed/', views.DetailedReportView.as_view(), name='detailed_report'),
    # path('utils/upload/', views.upload_shareholders, name='upload_shareholders'),
    # path('utils/update/', views.UpdateShareholdersView.as_view(), name='update_shareholders'),
    # path('utils/confirm/', views.confirm_shareholders, name='confirm_shareholders'),
    path('utils/updateprices/', views.SharePriceUpdateView.as_view(), name='update_prices')
]
