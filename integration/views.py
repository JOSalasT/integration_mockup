import os
import subprocess

from subprocess import Popen, PIPE
from django.shortcuts import render
from pyrml import RMLConverter
from rdflib import Graph
from tempfile import NamedTemporaryFile
from urllib.request import pathname2url

from integration_mockup.settings import BASE_DIR


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


def jarWrapper(*args):
    print(args)
    javaProcess = Popen(['java', '-jar'] + list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while javaProcess.poll() is None:
        line = javaProcess.stdout.readline()
        line = line.decode('utf-8')
        if line != '' and line.endswith("\n"):
            ret.append(line[:-1])
    stdout, stderr = javaProcess.communicate()
    ret += stdout.decode('utf-8').split('\n')
    if stderr != '':
        ret += stderr.decode('utf-8').split('\n')
    return ret


def process(request):
    if request.method == 'POST':
        ontology = request.POST.get('ontology')
        with request.FILES.get('rml_file') as rml_file:
            temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)
            template_vars = dict()
            temp_files = []
            for file in request.FILES.getlist('local_source'):
                temp_file = NamedTemporaryFile(mode='wb', delete=False)
                template_vars[file.name[:file.name.rfind(".")]] = pathname2url(temp_file.name)
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_files.append(temp_file)
            for chunk in rml_file.chunks():
                temp_string = chunk.decode('utf-8').replace('\r', '')
                for key, value in template_vars.items():
                    temp_string = temp_string.replace("{{ " + key + " }}", value)
                temp_rml_file.write(temp_string)
            temp_rml_file.seek(0)
        java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar", "rmlmapper-7.0.0-r374-all.jar")]
        rml_result = jarWrapper(*java_args)
        print(rml_result)
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
