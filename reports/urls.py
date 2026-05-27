from django.urls import path

from . import views

urlpatterns = [
    path("", views.report_index, name="report_index"),
    path("<slug:slug>/", views.report_detail, name="report_detail"),
]
