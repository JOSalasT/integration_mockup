import argparse
import os
import sys

import rdflib
import rdflib.term

from subprocess import run, PIPE

from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph
from tempfile import NamedTemporaryFile
import pathlib
from rdflib.exceptions import ParserError

BASE_DIR = "."
TEMP_DIR = "."


def jarWrapper(*args):
    javaProcess = run(['java', '-jar'] + list(args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
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


def ontology_to_RLS_with_triples(ontology_file):
    graph = Graph()
    tgds = []
    try:
        graph.parse(ontology_file, format='xml')
        restrictions = graph.subjects(rdflib.RDF.type, rdflib.OWL.Restriction)
        for object_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.ObjectProperty):
            property_domain = graph.objects(object_property, rdflib.RDFS.domain)
            for domain in property_domain:
                tgds.append(
                    "rdf_graph(?X,\'" + str(rdflib.RDF.type) + "\',\'" + str(domain) + "\') :- rdf_graph(?X,\'" + str(
                        object_property) + "\',?Y) .")
            property_ranges = graph.objects(object_property, rdflib.RDFS.range)
            for property_range in property_ranges:
                tgds.append("rdf_graph(?Y,\'" + str(rdflib.RDF.type) + "\',\'" + str(
                    property_range) + "\') :- rdf_graph(?X,\'" + str(
                    object_property) + "\',?Y) .")
            subproperties = graph.objects(object_property, rdflib.RDFS.subPropertyOf)
            for subproperty in subproperties:
                tgds.append("rdf_graph(?X,\'" + str(subproperty) + "\',?Y) :- rdf_graph(?X,\'" + str(
                    object_property) + "\',?Y) .")
        for class_property in graph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
            class_subclasses = graph.objects(class_property, rdflib.RDFS.subClassOf)
            for class_subclass in class_subclasses:
                if class_subclass in restrictions:
                    property_names = graph.objects(class_subclass, rdflib.OWL.onProperty)
                    for property_name in property_names:
                        tgds.append("rdf_graph(?X,\'" + str(property_name) + "\',!Z) :- rdf_graph(?X,\'" + str(
                            class_property) + "\',?Y) .")
                else:
                    tgds.append("rdf_graph(?X,\'" + str(rdflib.RDF.type) + "\',\'" + str(
                        class_subclass) + "\') :- rdf_graph(?X,\'" + str(rdflib.RDF.type) + "\',\'" + str(
                        class_property) + "\') .")
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


def remote_sparql_query(sparql_endpoint, query):
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    try:
        ret = sparql.queryAndConvert()
        ret.serialize(format="csv")
        return ret
    except Exception as e:
        print(e)


def rulewerkImportString(file_list, schema_list):
    temp_files = []
    schema_map = dict()
    ans = ""
    for file in schema_list:
        table_name = file.name[:file.name.rfind('.')]
        sql_injection = ""
        for chunk in file.chunks():
            sql_injection += chunk.decode('utf-8')
        schema_pairs = sql_injection[
                       sql_injection.rfind('(') + 1: sql_injection.rfind(')')].split(",")
        schema_map[table_name] = len(schema_pairs)
    for file in file_list:
        temp_file = copyFileToTemporaryFile(file)
        table_name = file.name[:file.name.rfind('.')]
        table_suffix = file.name.rsplit('.', 1)[1]
        temp_files.append(temp_file)
        if table_suffix == "csv":
            ans += "@source " + table_name + "[" + str(
                schema_map[table_name]) + "]" + " : load-csv(\"" + temp_file.name + "\") .\n"
    print(ans)


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--ontology", help="Path to ontology file", required=True)
parser.add_argument("-m", "--mapping", help="Path to RML file", required=True)
parser.add_argument("-q", "--query", help="Path to SPARQL query", required=False)
parser.add_argument("-s", "--sources", help="Path to local sources", required=False)
args = parser.parse_args()
ontology_tgds = ontology_to_RLS_with_triples("ontology.rdf")
if args.ontology is not None:
    ontology_tgds = ontology_to_RLS_with_triples(args.ontology)
query = "SELECT * WHERE {?s ?p ?o}"
if args.query is not None:
    query = args.query
rml_file = open("mapping.rml")
if args.mapping is not None:
    rml_file = open(args.mapping)
extension = "." + rml_file.name.rsplit('.', 1)[1]
source_files = os.listdir(args.sources) if args.sources is not None else []
template_vars = dict()
temp_files = []
rdf_files = []
rulewerk_script = ""
graph = rdflib.Graph()
for tgd in ontology_tgds:
    rulewerk_script += tgd + "\n"
for filename in source_files:
    table_name = filename[:filename.rfind('.')]
    file_extension = filename.rsplit('.', 1)[1]
    template_vars[table_name] = filename
    if file_extension == "rdf":
        graph += rdflib.Graph.parse(filename, format="xml")
    elif file_extension == "ttl":
        graph += rdflib.Graph.parse(filename, format="turtle")
    elif file_extension == "nt":
        graph += rdflib.Graph.parse(filename, format="n3")
for chunk in rml_file.readlines():
    temp_string = chunk.replace('\r', '')
    for key, value in template_vars.items():
        temp_string = temp_string.replace("{{ " + key + " }}", value)
java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar",
                          "rmlmapper-7.0.0-r374-all.jar"),
             "-m", rml_file.name]
rml_result = jarWrapper(*java_args)
graph += rdflib.Graph().parse(data=rml_result)
graph.serialize(destination="rml_result.nt", format='ntriples',
                encoding='utf-8')
rulewerk_script = "@source rdf_graph[3] : load-rdf(\"rml_result.nt\") .\n" + rulewerk_script
temp_rls_file = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
                                   dir=TEMP_DIR,
                                   suffix=".rls")
writeTextToTemporaryFile(temp_rls_file, rulewerk_script)
for file in temp_files:
    file.close()
java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "rulewerk",
                          "rulewerk-client-0.10.0.jar"), "--rule-file", temp_rls_file.name,
             "--query", "rdf_graph(?S,?P,?O)", "--print-complete-query-result"]
rulewerk_result = jarWrapper(*java_args)
result_text = ""
for line in rulewerk_result.splitlines():
    if line.strip().startswith('- ['):
        line = line.replace('- [', '').replace(']', '').replace(',', ' ')
        result_text += line + " .\n"
graph = rdflib.Graph().parse(data=result_text)
query_results = graph.query(query)
result_text = ""
for q in query_results:
    for v in query_results.vars:
        result_text += q.get(v) + "\n"
rml_file.close()
