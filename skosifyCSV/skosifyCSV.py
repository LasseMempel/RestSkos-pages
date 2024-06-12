import requests
import pandas as pd
import rdflib

"""
link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQCho2k88nLWrNSXj4Mgj_MwER5GQ9zbZ0OsO3X_QPa9s-3UkoeLLQHuNHoFMKqCFjWMMprKVHMZzOj/pub?gid=0&single=true&output=csv"
with open("data.csv", "w", encoding="utf-8") as f:
    f.write(requests.get(link).text)
"""
df = pd.read_csv("data.csv")
# create a skos graph from the csv
g = rdflib.Graph()
# create a namespace for the skos vocabulary
skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
# create namespaces for dcterms and description
terms = rdflib.Namespace("http://purl.org/dc/terms")
# create a namespacd for the concept scheme
scheme = rdflib.URIRef("http://LEIZA.org/scheme/conservation-restoration-thesaurus")
g.add((scheme, rdflib.RDF.type, skos.ConceptScheme))
g.add((scheme, terms.title, rdflib.Literal("Konservierungs- und Restaurierungsthesaurus")))
g.add((scheme, terms.creator, rdflib.Literal("LEIZA")))
g.add((scheme, terms.description, rdflib.Literal("Der mächtige Thesaurus für Konservierung und Restaurierung von Kulturgut.")))
g.add((scheme, terms.language, rdflib.Literal("de")))
# add the top concept
top = rdflib.URIRef("http://example.org/concept/top")
g.add((top, rdflib.RDF.type, skos.Concept))
g.add((top, skos.prefLabel, rdflib.Literal("Top")))
g.add((top, skos.inScheme, scheme))
# add the top concept to the scheme
g.add((scheme, skos.hasTopConcept, top))


# iterate over the rows of the csv
for index, row in df.iterrows():
    # create a skos concept with the label from the csv
    concept = rdflib.URIRef(f"http://LEIZA-Thesaurus.org/concept/{row['identifier']}")
    g.add((concept, rdflib.RDF.type, skos.Concept))
    g.add((concept, skos.prefLabel, rdflib.Literal(row["prefLabel"])))
    # add the broader concept if it exists
    if not pd.isna(row["parent"]) and not row["parent"]== "top":
        broader = rdflib.URIRef(f"http://example.org/concept/{row['parent']}")
        g.add((concept, skos.broader, broader))
# serialize the graph as turtle
g.serialize("data.ttl", format="turtle")






