import os
import re
import sys

import psycopg2
import rdflib
import rdflib.term

from subprocess import run, PIPE

from SPARQLWrapper import SPARQLWrapper
from django.db import connection
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

def query_predicates_map(query_string):
    term_map = dict()
    prefix_map = dict()
    # Find all declared prefixes.
    prefix_terms = re.findall(r"""(?i)\b(?:PREFIX|prefix) (\w+):\s+<((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\((?:[^\s()<>]+|\([^\s()<>]+\))*\))+(?:\((?:[^\s()<>]+|\([^\s()<>]+\))*\)|[^\s`!()\[\]{};:'"., !=?«»“”‘’]))>""",query_string)
    # Find all IRIs and prefixes + suffixes in the query.
    terms = re.findall(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,
    4}/)(?:[^\s()<>]+|\((?:[^\s()<>]+|\([^\s()<>]+\))*\))+(?:\((?:[^\s()<>]+|\([^\s()<>]+\))*\)|[^\s`!()\[\]{};:'".,
    <>?«»“”‘’]))""", query_string)
    for prefix in prefix_terms:
        prefix_map[prefix[0]] = prefix[1]
    for term in terms:
        split_term = re.split(r"\W", term)
        predicate_name = split_term[-1]
        if not predicate_name == "":
            if split_term[0] in prefix_map:
                term_map[predicate_name] = prefix_map[split_term[0]] + predicate_name
            else:
                term_map[predicate_name] = term
    return term_map

predicates_to_iri = query_predicates_map("""PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dc:   <http://purl.org/dc/elements/1.1/>
PREFIX :     <http://example/ns#>

SELECT ?book ?title
WHERE
{ ?t rdf:subject    ?book  .
  ?t rdf:predicate  dc:title .
  ?t rdf:object     ?title .
  ?t :saidBy        "Bob" .
  ?t <http://example/ns#saidTo> "Alice" .
}""")

ontology_file = open("ontology.rdf")
query = ""
rml_file = open("mapping.rml")
extension = "." + rml_file.name.rsplit('.', 1)[1]
source_files = sys.argv[1:]
template_vars = dict()
temp_files = []
rdf_files = []
rulewerk_script = ""
graph = rdflib.Graph()
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
    temp_files.append(open(filename))
graph.serialize(destination="merged_graph.ttl", format="turtle")
java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar",
                          "rmlmapper-7.0.0-r374-all.jar"),
             "-m", rml_file.name]
rml_result = jarWrapper(*java_args)
java_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "jar",
                          "tw-rewriting.jar"),
             "ontology.rdf", "query"]
tw_rewriting_result = jarWrapper(*java_args)
graph += rdflib.Graph().parse(data=rml_result)
connection = psycopg2.connect(database="postgres", user="postgres", password="", host="localhost", port="5432")
with connection.cursor() as cursor:
    schema_map = dict()
    for file in temp_files:
        table_name = file.name[:file.name.rfind('.')]
        sql_injection = ""
        schema_file = open(str(file) + ".sql")
        for line in schema_file.readlines():
            sql_injection += line
        schema_pairs = sql_injection[
                       sql_injection.rfind('(') + 1: sql_injection.rfind(')')].split(",")
        columns = []
        for pair in schema_pairs:
            column_name = pair.strip().split(" ")[0]
            columns.append(column_name)
        schema_map[table_name] = columns
        cursor.execute(sql_injection)  # TODO I know this is extremely dangerous. This is only
        # for a controlled demo.
    for file in temp_files:
        table_name = file.name[:file.name.rfind('.')]
        for line in file.readlines()[1:]:
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
temp_results = NamedTemporaryFile(mode='w+', encoding='utf-8', newline="\n", delete=False,
                                  dir=TEMP_DIR,
                                  suffix=".csv")
ontop_args = [os.path.join(BASE_DIR, "integration_mockup", "static", "systems", "ontop",
                           "ontop.bat"), "query", "-m", rml_file, "-t",
              ontology_file, "-q", query,
              "-p", "integration_mockup/static/systems/ontop/properties.txt",
              "-a", "merged_graph.ttl",
               "-o",
              pathForOntop(temp_results.name)
              ]
ontop_process = run(ontop_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
print(ontop_process.stdout.decode('utf-8'))
print(ontop_process.stderr.decode('utf-8'))
for file in temp_files:
    file.close()
    os.remove(file.name)
result_text = ""
for line in temp_results.readlines():
    result_text += line
