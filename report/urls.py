from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    # Reports
    path('report/date_short/', views.date_short_report, name='date_short_report'),
    path('report/company/', views.CompanyReportView.as_view(), name='company_report'),
    path('report/detailed/', views.DetailedReportView.as_view(), name='detailed_report'),
    path('report/current_holdings/', views.CurrentHoldingsView.as_view(), name='current_holdings'),
    path('report/shares_info/', views.SharesInfoView.as_view(), name='shares_info'),
    path('report/quarter/', views.QuarterGraphslView.as_view(), name='quarter_report'),
    path('report/category_performance/', views.CategoryPerformanceView.as_view(), name='category_performance_report'),
    # Utils
    path('utils/upload/', views.upload_shareholders, name='upload_shareholders'),
    path('utils/update/', views.UpdateShareholdersView.as_view(), name='update_shareholders'),
    path('utils/confirm/', views.confirm_shareholders, name='confirm_shareholders'),
    path('utils/updateprices/', views.SharePriceUpdateView.as_view(), name='update_prices'),
    path('utils/sharescontrol/', views.SharesControlView.as_view(), name='shares_control'),
]
