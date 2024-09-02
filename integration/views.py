import os

import rdflib
import rdflib.term

from subprocess import run, PIPE

from django.shortcuts import render
from django.db import connection
from rdflib import Graph
from tempfile import NamedTemporaryFile
import pathlib

from rdflib.exceptions import ParserError

from integration_mockup.settings import BASE_DIR, TEMP_DIR

JRE = "C:\\Program Files (x86)\\Java\\jre1.8.0_421\\bin\\java.exe"
ONTOP_HOME = os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop", "ontop")


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


def writeTextToTemporaryFile(temporaryFile, text):
    for line in text.splitlines():
        temporaryFile.write(line + "\n")
    temporaryFile.seek(0)


def copyFileToTemporaryFile(file):
    extension = "." + file.name.rsplit('.', 1)[1]
    temp_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR,
                                   suffix=extension)
    for chunk in file.chunks():
        temp_file.write(chunk.decode('utf-8'))
    temp_file.seek(0)
    return temp_file


def fileToString(file):
    text = ""
    for chunk in file.chunks():
        text += chunk.decode('utf-8').replace("\r\n", "\n")
    return text


def pathForOntop(filename):
    return pathlib.Path(filename).relative_to(BASE_DIR).as_posix()


# def process(request):
#     if request.method == 'POST':
#         temp_ontology = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
#                                            dir=TEMP_DIR)  # TODO Need to support other formats e.g. Turtle, NTriples
#         rml_graph = rdflib.Graph()
#         temp_rdf_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
#                                            dir=TEMP_DIR, suffix="ttl")
#         if 'ontology' in request.POST:
#             ontology = request.POST.get('ontology')
#             writeTextToTemporaryFile(temp_ontology, ontology)
#         with request.FILES.get('rml_file') as rml_file:
#             extension = "." + rml_file.name.rsplit('.', 1)[1]
#             temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR,
#                                                suffix=extension)
#             template_vars = dict()
#             temp_files = []
#             for file in request.FILES.getlist('local_source'):
#                 temp_file = copyFileToTemporaryFile(file)
#                 table_name = file.name[:file.name.rfind('.')]
#                 template_vars[table_name] = temp_file.name
#                 temp_files.append(temp_file)
#             for chunk in rml_file.chunks():
#                 temp_string = chunk.decode('utf-8').replace('\r', '')
#                 for key, value in template_vars.items():
#                     temp_string = temp_string.replace("{{ " + key + " }}", value)
#                 temp_rml_file.write(temp_string)
#             temp_rml_file.seek(0)
#             java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar", "rmlmapper-7.0.0-r374-all.jar"),
#                          "-m", temp_rml_file.name]
#             rml_result = jarWrapper(*java_args)
#             for line in rml_result.splitlines():
#                 print(line)
#                 temp_rdf_file.write(line + " . \n")
#             temp_rml_file.close()
#             os.remove(temp_rml_file.name)
#             for file in temp_files:
#                 file.close()
#                 os.remove(file.name)
#         if "data_source" in request.POST:
#             for i in range(len(request.POST.get("data_source"))):
#                 print("something")
#         if "system" in request.POST:
#             system = request.POST.get('system')
#             if request.POST.get('integration_type') == "forward":
#                 print("materialise")
#                 if system == "RDFox":
#                     print("Running RDFox")
#                 elif system == "Rulewerk":
#                     print("Running Rulewerk")
#                 elif system == "Ontop":
#                     print("Running Ontop")
#                     ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop", "ontop"),
#                                   "materialize"]
#                     result = run(list(ontop_args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
#                     print(result.stdout.decode('utf-8'))
#                 else:
#                     print("Unknown system")
#             elif request.POST.get('integration_type') == "backward":
#                 temp_query = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR)
#                 query = request.POST.get('query_text')
#                 writeTextToTemporaryFile(temp_query, query)
#                 if system == "Rapid":
#                     print("Running Rapid")
#                 elif system == "Iqaros":
#                     print("Running Iqaros")
#                 elif system == "Graal":
#                     print("Running Graal")
#                 elif system == "GQR":
#                     print("Running GQR")
#                 elif system == "OntopRW":
#                     print("Running OntopRW")
#                     ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "tw-rewriting",
#                                                "tw-rewriting.jar"), temp_ontology.name, temp_query.name]
#                     ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
#                                 "ontop.bat"), "query", "-a", temp_rdf_file.name, "-t",
#                                   temp_ontology.name, "-q", temp_query.name, "-p",
#                                   os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
#                                                "properties.txt")
#                                   ]
#                     ontop_process = run(ontop_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
#                     print(ontop_process.stdout.decode('utf-8'))
#                     print(ontop_process.stderr.decode('utf-8'))
#                 elif system == "CGQR":
#                     print("Running CGQR")
#                 else:
#                     print("Unknown system")
#                 temp_query.close()
#                 os.remove(temp_query.name)
#             else:
#                 print(request.POST.get('integration_type'))
#             temp_ontology.close()
#             os.remove(temp_ontology.name)
#
#     return render(request, 'steps/upload_ontology.html')

def ontology_to_tgds(ontology_file):
    graph = Graph()
    tgds = []
    try:
        graph.parse(ontology_file, format='xml')
        restrictions = graph.subjects(rdflib.RDF.type, rdflib.OWL.Restriction)
        for object_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty):
            property_domain = graph.objects(object_property, rdflib.RDFS.domain)
            for domain in property_domain:
                tgds.append(str(object_property) + "(x,y) -> " + str(domain) + "(x) .")
            property_ranges = graph.objects(object_property, rdflib.RDFS.range)
            for property_range in property_ranges:
                tgds.append(str(object_property) + "(x,y) -> " + str(property_range) + "(y) .")
            subproperties = graph.objects(object_property, rdflib.RDFS.subPropertyOf)
            for subproperty in subproperties:
                tgds.append(str(object_property) + "(x,y) -> " + str(subproperty) + "(x,y) .")
        for class_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
            class_subclasses = graph.objects(class_property, rdflib.RDFS.subClassOf)
            for class_subclass in class_subclasses:
                if class_subclass in restrictions:
                    property_names = graph.objects(class_subclass, rdflib.OWL.onProperty)
                    for property_name in property_names:
                        tgds.append(str(class_property) + "(x) -> " + str(property_name) + "(x,z) .")
                else:
                    tgds.append(str(class_property) + "(x) -> " + str(class_subclass) + "(x) .")
        return tgds
    except ParserError as e:
        print(e)
        return None


def ontology_to_RLS(ontology_file):
    graph = Graph()
    tgds = []
    try:
        graph.parse(ontology_file, format='xml')
        restrictions = graph.subjects(rdflib.RDF.type, rdflib.OWL.Restriction)
        for object_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty):
            property_domain = graph.objects(object_property, rdflib.RDFS.domain)
            for domain in property_domain:
                tgds.append(str(domain) + "(?X) :- " + str(object_property) + "(?X,?Y) .")
            property_ranges = graph.objects(object_property, rdflib.RDFS.range)
            for property_range in property_ranges:
                tgds.append(str(property_range) + "(?Y) :- " + str(object_property) + "(?X,?Y) .")
            subproperties = graph.objects(object_property, rdflib.RDFS.subPropertyOf)
            for subproperty in subproperties:
                tgds.append(str(subproperty) + "(?X,?Y) :- " + str(object_property) + "(?X,?Y) .")
        for class_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
            class_subclasses = graph.objects(class_property, rdflib.RDFS.subClassOf)
            for class_subclass in class_subclasses:
                if class_subclass in restrictions:
                    property_names = graph.objects(class_subclass, rdflib.OWL.onProperty)
                    for property_name in property_names:
                        tgds.append(str(property_name) + "(?X,!Z) :- " + str(class_property) + "(?X,?Y) .")
                else:
                    tgds.append(str(class_subclass) + "(?Y) :- " + str(class_property) + "(?X,?Y) .")
        return tgds
    except ParserError as e:
        print(e)
        return None


def rulewerk_process(ontology, rdf_file, query):
    print("Running OntopRW")
    ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "tw-rewriting",
                               "tw-rewriting.jar"), ontology.name, query.name]
    ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
                               "ontop.bat"), "query", "-a", rdf_file.name, "-t",
                  ontology.name, "-q", query.name, "-p",
                  os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
                               "properties.txt")
                  ]
    ontop_process = run(ontop_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    print(ontop_process.stdout.decode('utf-8'))
    print(ontop_process.stderr.decode('utf-8'))


def process(request):
    if request.method == 'POST':
        temp_ontology = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
                                           dir=TEMP_DIR,
                                           suffix=".owl")  # TODO Need to support other formats e.g. Turtle, NTriples
        if 'ontology' in request.POST:
            ontology = request.POST.get('ontology')
            writeTextToTemporaryFile(temp_ontology, ontology)
        if "system" in request.POST:
            system = request.POST.get('system')
            if request.POST.get('integration_type') == "forward":
                print("materialise")
                if system == "RDFox":
                    print("Running RDFox")
                elif system == "Rulewerk":
                    print("Running Rulewerk")
                    ontology_tgds = ontology_to_RLS(temp_ontology)
                    with request.FILES.get('rml_file') as rml_file:
                        extension = "." + rml_file.name.rsplit('.', 1)[1]
                        temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR,
                                                           suffix=extension)
                        template_vars = dict()
                        temp_files = []
                        for file in request.FILES.getlist('local_source'):
                            temp_file = copyFileToTemporaryFile(file)
                            table_name = file.name[:file.name.rfind('.')]
                            template_vars[table_name] = temp_file.name
                            temp_files.append(temp_file)
                        for chunk in rml_file.chunks():
                            temp_string = chunk.decode('utf-8').replace('\r', '')
                            for key, value in template_vars.items():
                                temp_string = temp_string.replace("{{ " + key + " }}", value)
                            temp_rml_file.write(temp_string)
                        temp_rml_file.seek(0)
                        java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar", "rmlmapper-7.0.0-r374-all.jar"),
                                     "-m", temp_rml_file.name]
                        rml_result = jarWrapper(*java_args)
                        print(rml_result)
                elif system == "Ontop":
                    print("Running Ontop")
                    ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop", "ontop"),
                                  "materialize"]
                    result = run(list(ontop_args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    print(result.stdout.decode('utf-8'))
                else:
                    print("Unknown system")
            elif request.POST.get('integration_type') == "backward":
                temp_query = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False, dir=TEMP_DIR)
                query = request.POST.get('query_text')
                writeTextToTemporaryFile(temp_query, query)
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
                    with request.FILES.get('rml_file') as rml_file:
                        extension = "." + rml_file.name.rsplit('.', 1)[1]
                        temp_rml_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
                                                           dir=TEMP_DIR,
                                                           suffix=extension)
                        template_vars = dict()
                        temp_files = []
                        with connection.cursor() as cursor:
                            schema_map = dict()
                            for file in request.FILES.getlist('schema'):
                                table_name = file.name[:file.name.rfind('.')]
                                sql_injection = ""
                                for chunk in file.chunks():
                                    sql_injection += chunk.decode('utf-8')
                                schema_pairs = sql_injection[
                                               sql_injection.rfind('(') + 1: sql_injection.rfind(')')].split(",")
                                columns = []
                                for pair in schema_pairs:
                                    column_name = pair.strip().split(" ")[0]
                                    columns.append(column_name)
                                schema_map[table_name] = columns
                                cursor.execute(sql_injection)  # TODO I know this is extremely dangerous. This is only
                                # for a controlled demo.
                            for file in request.FILES.getlist('local_source'):
                                text = fileToString(file)
                                table_name = file.name[:file.name.rfind('.')]
                                for line in text.splitlines()[1:]:
                                    columns = schema_map[table_name]
                                    values = line.split(",")
                                    column_string = "("
                                    values_string = "("
                                    for i in range(len(values)):
                                        value = values[i]
                                        if not value == "":
                                            column_string += columns[i] + ","
                                            values_string += value + ","
                                    column_string = column_string[:-1] + ")"
                                    values_string = values_string[:-1] + ")"
                                    cursor.execute(
                                        "INSERT INTO " + table_name + column_string + " VALUES" + values_string)
                        for chunk in rml_file.chunks():
                            temp_string = chunk.decode('utf-8').replace('\r', '')
                            for key, value in template_vars.items():
                                temp_string = temp_string.replace("{{ " + key + " }}", value)
                            temp_rml_file.write(temp_string)
                        temp_rml_file.seek(0)
                        temp_results = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
                                                          dir=TEMP_DIR,
                                                          suffix=".csv")
                        ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
                                                   "ontop.bat"), "query", "-m", pathForOntop(temp_rml_file.name), "-t",
                                      pathForOntop(temp_ontology.name), "-q", pathForOntop(temp_query.name), "-p",
                                      "integration_mockup/static/systems/ontop/properties.txt", "-o",
                                      pathForOntop(temp_results.name)
                                      ]
                        ontop_process = run(ontop_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        print(ontop_process.stdout.decode('utf-8'))
                        print(ontop_process.stderr.decode('utf-8'))
                        for file in temp_files:
                            file.close()
                            os.remove(file.name)
                        temp_rml_file.close()
                        os.remove(temp_rml_file.name)
                        temp_ontology.close()
                        os.remove(temp_ontology.name)
                        temp_query.close()
                        result_text = ""
                        for line in temp_results.readlines():
                            result_text += line
                        return render(request, 'steps/query_results.html', {"results": result_text, system: system})
                elif system == "CGQR":
                    print("Running CGQR")
                else:
                    print("Unknown system")
                temp_query.close()
                os.remove(temp_query.name)
            else:
                print(request.POST.get('integration_type'))

    return render(request, 'steps/upload_ontology.html')
# Create your views here.
