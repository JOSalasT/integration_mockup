from django.shortcuts import render
from django.views.generic import ListView


def index(request):
    return render(request, 'steps/upload_ontology.html')

# Create your views here.
