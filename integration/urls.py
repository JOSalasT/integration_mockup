from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("graph", views.rml_mapping, name="rml_mapping"),
    path("result", views.process, name="process")
]
