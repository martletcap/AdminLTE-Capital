from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.short_report, name='index'),
    # Reports
    path('report/short/', views.short_report, name='short_report'),
    path('report/company/', views.CompanyReportView.as_view(), name='company_report'),
    path('report/detailed/', views.DetailedReportView.as_view(), name='detailed_report'),
    path('report/current_holdings/', views.CurrentHoldingsView.as_view(), name='current_holdings'),
    path('report/shares_info/', views.SharesInfoView.as_view(), name='shares_info'),
    # Utils
    path('utils/upload/', views.upload_shareholders, name='upload_shareholders'),
    path('utils/update/', views.UpdateShareholdersView.as_view(), name='update_shareholders'),
    path('utils/confirm/', views.confirm_shareholders, name='confirm_shareholders'),
    path('utils/updateprices/', views.SharePriceUpdateView.as_view(), name='update_prices'),
    path('utils/sharescontrol/', views.SharesControlView.as_view(), name='shares_control'),
    path('utils/parse_shareholders/', views.ParseShareholders.as_view(), name='parse_shareholders'),
]
