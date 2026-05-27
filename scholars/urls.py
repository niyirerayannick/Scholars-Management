from django.urls import path

from . import views

urlpatterns = [
    path("", views.scholar_list, name="scholar_list"),
    path("add/", views.scholar_create, name="scholar_add"),
    path("<int:pk>/", views.scholar_detail, name="scholar_detail"),
    path("<int:pk>/edit/", views.scholar_update, name="scholar_edit"),
    path("<int:pk>/delete/", views.scholar_delete, name="scholar_delete"),
]
