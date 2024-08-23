import os
import subprocess

from subprocess import Popen, PIPE
from django.shortcuts import render
from pyrml import RMLConverter
from rdflib import Graph
from tempfile import NamedTemporaryFile
from urllib.request import pathname2url


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

    return render(request, 'steps/display_mapping.html')


def process(request):
    if request.method == 'POST':
        ontology = request.POST.get('ontology')
        with request.FILES.get('rml_file') as rml_file:
            temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)
            for chunk in rml_file.chunks():
                temp_string = chunk.decode('utf-8')
                temp_rml_file.write(temp_string)
            temp_rml_file.close()
            for file in request.FILES.getlist('local_source'):
                temp_file = NamedTemporaryFile()
                for chunk in file.chunks():
                    temp_file.write(chunk)
            rml_converter = RMLConverter()
            rdf_graph = rml_converter.convert(pathname2url("media/rml_example.rml"))
            rdf_graph = rml_converter.convert(pathname2url(temp_rml_file.name))
            for s, p, o in rdf_graph:
                print(str(s) + "," + str(p) + "," + str(o))
        if "data_source" in request.POST:
            for i in range(len(request.POST.get("data_source"))):
                print("something")
        if "system" in request.POST:
            print("system")
            system = request.POST.get('system')
            if request.POST.get('next') == "Materialise":
                print("materialise")
                if system == "RDFox":
                    print("Running RDFox")
                elif system == "Rulewerk":
                    print("Running Rulewerk")
                else:
                    print("Unknown system")
            elif request.POST.get('next') == "Run query":
                print("run query")
                if system == "Rapid":
                    print("Running Rapid")
                elif system == "Iqaros":
                    print("Running Iqaros")
                elif system == "Graal":
                    print("Running Graal")
                elif system == "GQR":
                    print("Running GQR")
                elif system == "OntopRW":
                    print("Running OntopRW")
                    process = Popen(['java', '-jar', 'tika-app-1.24.1.jar', '-t', '42250_EN_Upload.docx'], stdout=PIPE,
                                    stderr=PIPE)
                    result = process.communicate()
                elif system == "CGQR":
                    print("Running CGQR")
                else:
                    print("Unknown system")
            else:
                print("unknown next value")

    return render(request, 'steps/upload_ontology.html')
# Create your views here.
