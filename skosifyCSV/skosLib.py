import requests
import pandas as pd
import urllib.parse
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import SKOS, RDF, DC, DCTERMS, RDFS

def csv2Df(link, propertyMatchDict):
    with open("data.csv", "w", encoding="utf-8") as f:
        f.write(requests.get(link).text.encode("ISO-8859-1").decode())
    df = pd.read_csv('data.csv', encoding="utf-8")
    df.rename(columns=propertyMatchDict, inplace=True) # rename columns according to propertyMatchDict
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x) # remove leading and trailing whitespaces from all cells
    return df

def df2Skos(df, baseLanguageLabel, baseUri, seperator):
    propertyTuples = [
        ("notation", SKOS.notation, Literal, False),
        ("prefLabel", SKOS.prefLabel, Literal, True),
        ("altLabel", SKOS.altLabel, Literal, True),
        ("definition", SKOS.definition, Literal, True),
        ("broader", SKOS.broader, URIRef, False),
        ("narrower", SKOS.narrower, URIRef, False),
        ("related", SKOS.related, URIRef, False),
        ("closeMatch", SKOS.closeMatch, URIRef, False),
        ("relatedMatch", SKOS.relatedMatch, URIRef, False),
        ("exactMatch", SKOS.exactMatch, URIRef, False)
    ]

    extendedTuples = [
        ("source", DC.source, Literal, False),
        ("creator", DC.creator, Literal, False),
        ("seeAlso", RDFS.seeAlso, Literal, False)
    ]

    g = Graph()
    thesaurus = URIRef(baseUri)
    thesaurusAddendum = URIRef(thesaurus + "/")

    g.add ((thesaurus, RDF.type, SKOS.ConceptScheme))
    g.add ((thesaurus, DC.title, Literal("Leiza Restaurierungs- und Konservierungsthesaurus", lang=baseLanguageLabel)))
    g.add ((thesaurus, DC.description, Literal("Der Leiza Restaurierungs- und Konservierungsthesaurus für archäologische Kulturgüter", lang=baseLanguageLabel)))

    for index, row in df.iterrows():
        if row["prefLabel"] and isinstance(row["prefLabel"], str) and row["notation"] and isinstance(row["notation"], str):
            print(row["prefLabel"], row["notation"])
            concept = URIRef(thesaurusAddendum + row['notation'])
            g.add ((concept, RDF.type, SKOS.Concept))
            for prop, pred, obj, isLang in propertyTuples+extendedTuples:
                if prop in df.columns:
                    if not isinstance(row[prop], float):
                        if seperator in row[prop]:
                            for i in row[prop].split(seperator):
                                i = i.strip()
                                print(i)
                                if obj == URIRef:
                                    if pred in [SKOS.broader, SKOS.narrower, SKOS.related]:
                                        g.add ((concept, pred, URIRef(thesaurusAddendum + i)))
                                    else:
                                        g.add ((concept, pred, URIRef(urllib.parse.quote(i))))
                                else:
                                    if isLang:
                                        g.add ((concept, pred, obj(i, lang= baseLanguageLabel)))
                                    else:
                                        g.add ((concept, pred, obj(i)))
                                if isLang:
                                    g.add ((concept, pred, obj(i, lang= baseLanguageLabel)))
                                else:
                                    g.add ((concept, pred, obj(i)))
                        else:
                            if obj == URIRef:
                                if pred in [SKOS.broader, SKOS.narrower, SKOS.related]:
                                    g.add ((concept, pred, URIRef(thesaurusAddendum + row[prop])))
                                else:
                                    g.add ((concept, pred, URIRef(urllib.parse.quote(row[prop]))))
                            else:
                                if isLang:
                                    g.add ((concept, pred, obj(row[prop], lang= baseLanguageLabel)))
                                else:
                                    g.add ((concept, pred, obj(row[prop])))
            g.add ((concept, SKOS.inScheme, thesaurus))
            if row["broader"] == "top":
                g.add ((thesaurus, SKOS.hasTopConcept, concept))
                g.add ((concept, SKOS.topConceptOf, thesaurus))

    return g


def main(link, baseLanguageLabel, propertyMatchDict, seperator):
    """
    df = csv2Df(link, propertyMatchDict)
    text = df.to_csv(index=False)
    with open('polishedData.csv', 'w', encoding="utf-8") as f:
        f.write(text)
    """
    df = pd.read_csv('polishedData.csv', encoding="utf-8")
    graph = df2Skos(df, baseLanguageLabel, baseUri, seperator)
    graph.serialize(destination='thesaurus.ttl', format='turtle')   


link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQCho2k88nLWrNSXj4Mgj_MwER5GQ9zbZ0OsO3X_QPa9s-3UkoeLLQHuNHoFMKqCFjWMMprKVHMZzOj/pub?gid=0&single=true&output=csv"
baseLanguageLabel = "de"
baseUri = "https://archaeology.link/conservationthesaurus"

# dictionary to map divergent column names in the csv to the SKOS properties
propertyMatchDict = {"identifier":"notation","description":"definition","parent":"broader"}
seperator = "|"

main(link, baseLanguageLabel, propertyMatchDict, seperator)