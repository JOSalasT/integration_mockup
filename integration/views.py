from django.shortcuts import render
from django.views.generic import ListView


def index(request):
    return render(request, 'steps/upload_ontology.html')

def process(request):
    if request.method == 'POST':
        ontology = request.POST.get('ontology')
        for i in range(len(request.POST.get("data_source"))):
            print("something")
        for i in range(len(request.POST.get("local_source"))):
            print("reading")
        if request.POST.get('next') == "Materialise":
            print("materialise")
        elif request.POST.get('next') == "Run query":
            print("run query")
        else:
            print("unknown next value")
    return render(request, 'steps/upload_ontology.html')
# Create your views here.
