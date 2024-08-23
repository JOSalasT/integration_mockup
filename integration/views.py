from django.shortcuts import render
from pyrml import RMLConverter
from rdflib import Graph
from django.views.generic import ListView


def index(request):
    return render(request, 'steps/upload_ontology.html')

def rml_mapping(request):
    if request.method == 'POST':
        rml_file = request.FILES['rml_file']
        rdf_graph = Graph()
        rdf_graph.parse(rml_file, format='ttl')
        nodes = []
        edges = []
        for s, p, o in rdf_graph:
            node1 = s
            nodes.append()
            edge = p
            node2 = o

    return render(request,'steps/display_mapping.html')

# Create your views here.
