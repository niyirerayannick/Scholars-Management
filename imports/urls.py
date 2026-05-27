from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload_excel, name="import_upload"),
    path("sample-template/", views.sample_template, name="import_sample_template"),
]
