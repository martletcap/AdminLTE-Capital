from django.urls import path, include

from . import views


urlpatterns = [
    path('/report_short/', views.report_short, name='report_short'),
]
