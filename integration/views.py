import os
import time

from subprocess import run, Popen, PIPE

import rdflib
from django.shortcuts import render
from rdflib import Graph
from tempfile import NamedTemporaryFile
from urllib.request import pathname2url

from integration_mockup.settings import BASE_DIR, TEMP_DIR


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
            edge = p
            node2 = o

    return render(request, 'steps/display_mapping.html')


def jarWrapper(*args):
    print(*args)
    javaProcess = run(['java', '-jar'] + list(args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # while javaProcess.poll() is None:
    #     line = javaProcess.stdout.readline()
    #     line = line.decode('utf-8')
    #     if line != '' and line.endswith("\n"):
    #         ret.append(line[:-1])
    # stdout, stderr = javaProcess.communicate()
    # ret += stdout.decode('utf-8').split('\n')
    # if stderr != '':
    #     ret += stderr.decode('utf-8').split('\n')
    return javaProcess.stdout.decode('utf-8')


def process(request):
    if request.method == 'POST':
        ontology = request.POST.get('ontology').encode('utf-8')
        ontology_graph = rdflib.Graph()
        ontology_graph.parse(ontology, format='xml')
        for s, p, o in ontology_graph:
            print(str(s) + "," + str(p) + "," + str(o))
        with request.FILES.get('rml_file') as rml_file:
            extension = "." + rml_file.name.rsplit('.', 1)[1]
            temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR, suffix=extension)
            template_vars = dict()
            temp_files = []
            for file in request.FILES.getlist('local_source'):
                temp_extension = "." + file.name.rsplit('.', 1)[1]
                temp_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR, suffix=temp_extension)
                template_vars[file.name[:file.name.rfind(".")]] = temp_file.name
                for chunk in file.chunks():
                    temp_file.write(chunk.decode('utf-8'))
                temp_files.append(temp_file)
                temp_file.seek(0)
            for chunk in rml_file.chunks():
                temp_string = chunk.decode('utf-8').replace('\r', '')
                for key, value in template_vars.items():
                    temp_string = temp_string.replace("{{ " + key + " }}", value)
                temp_rml_file.write(temp_string)
            temp_rml_file.seek(0)
            java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar", "rmlmapper-7.0.0-r374-all.jar"), "-m", temp_rml_file.name]
            rml_result = jarWrapper(*java_args)
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
                    process = run(['java', '-jar', 'tika-app-1.24.1.jar', '-t', '42250_EN_Upload.docx'])
                    result = process.communicate()
                elif system == "CGQR":
                    print("Running CGQR")
                else:
                    print("Unknown system")
            else:
                print("unknown next value")

    return render(request, 'steps/upload_ontology.html')
# Create your views here.
