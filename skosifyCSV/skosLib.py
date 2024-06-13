import requests
import pandas as pd
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import SKOS, RDF

with open ('data.csv', 'r', encoding="utf-8") as f:
    with open("fixedData.csv", "w", encoding="utf-8") as ff:
        # repair wrong encoded german umlauts
        for line in f:
            ff.write(line.replace("Ã¼", "ü").replace("Ã¶", "ö").replace("Ã¤", "ä").replace("ÃŸ", "ß").replace("Ã„", "Ä").replace("Ã–", "Ö").replace("Ãœ", "Ü").replace("Ã", "ß"))

df = pd.read_csv('fixedData.csv')

g = Graph()
# use the SKOS namespace
# skos:ConceptScheme, skos:Concept, skos:prefLabel, skos:broader, skos:related, skos:altLabel, skos:definition, skos:hasTopConcept

thesaurus = URIRef("http://leiza.de/thesaurus/")
g.add ((thesaurus, RDF.type, SKOS.ConceptScheme))


for index, row in df.iterrows():
    if not pd.isnull(row["prefLabel"]):
        concept = URIRef(thesaurus + str(row['identifier']))
        g.add ((concept, RDF.type, SKOS.Concept))
        g.add ((concept, SKOS.prefLabel, Literal(row['prefLabel'])))
        if not pd.isnull(row["altLabel"]):
            if "|" in str(row["altLabel"]):
                for i in str(row["altLabel"]).split("|"):
                    g.add ((concept, SKOS.altLabel, Literal(i)))
            else:
                g.add ((concept, SKOS.altLabel, Literal(row["altLabel"])))
        if not pd.isnull(row["description"]):
            g.add ((concept, SKOS.definition, Literal(row['description'])))
        if not pd.isnull(row['parent']) and not row["parent"] == "" :
            broader = URIRef(thesaurus + row['parent'])
            g.add ((concept, SKOS.broader, broader))
        if not pd.isnull(row['related']):
            related = URIRef(thesaurus + row['related'])
            g.add ((concept, SKOS.related, related))
        g.add ((concept, SKOS.inScheme, thesaurus))
        if row["parent"] == "top":
            g.add ((thesaurus, SKOS.hasTopConcept, concept))
            g.add ((concept, SKOS.topConceptOf, thesaurus))

#g.serialize(destination='fixedData.rdf', format='xml')
g.serialize(destination='fixedData.ttl', format='turtle')
