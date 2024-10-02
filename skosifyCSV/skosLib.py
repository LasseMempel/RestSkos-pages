import requests
import pandas as pd
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import SKOS, RDF, DC, DCTERMS, RDFS

link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQCho2k88nLWrNSXj4Mgj_MwER5GQ9zbZ0OsO3X_QPa9s-3UkoeLLQHuNHoFMKqCFjWMMprKVHMZzOj/pub?gid=0&single=true&output=csv"
with open("data.csv", "w", encoding="utf-8") as f:
    f.write(requests.get(link).text)
with open ('data.csv', 'r', encoding="utf-8") as f:
    with open("fixedData.csv", "w", encoding="utf-8") as ff:
        # repair wrong encoded german umlauts
        for line in f:
            ff.write(line.replace("Ã¼", "ü").replace("Ã¶", "ö").replace("Ã¤", "ä").replace("ÃŸ", "ß").replace("Ã„", "Ä").replace("Ã–", "Ö").replace("Ãœ", "Ü").replace("Ã", "ß").replace("Ã", "Ü").replace("â", "—"))
df = pd.read_csv('fixedData.csv', encoding="utf-8")
languageLabel = "@de"
g = Graph()
thesaurus = URIRef("www.leiza.de/thesaurus")
thesaurusAddendum = thesaurus + "/"
g.add ((thesaurus, RDF.type, SKOS.ConceptScheme))
g.add ((thesaurus, DC.title, Literal("Leiza Restaurierungs- und Konservierungsthesaurus")+languageLabel))
g.add ((thesaurus, DC.description, Literal("Der mächtige Leiza Restaurierungs- und Konservierungsthesaurus")+languageLabel))
for index, row in df.iterrows():
    if not pd.isnull(row["prefLabel"]):
        concept = URIRef(thesaurusAddendum + str(row['identifier']))
        g.add ((concept, SKOS.notation, Literal(str(row['identifier']))))
        g.add ((concept, RDF.type, SKOS.Concept))
        g.add ((concept, SKOS.prefLabel, Literal(row['prefLabel'] + languageLabel)))
        if not pd.isnull(row["altLabel"]):
            if "|" in str(row["altLabel"]):
                for i in str(row["altLabel"]).split("|"):
                    g.add ((concept, SKOS.altLabel, Literal(i.strip() + languageLabel)))
            else:
                g.add ((concept, SKOS.altLabel, Literal(row["altLabel"] + languageLabel)))

        if not pd.isnull(row["seeAlso"]):
            if "|" in str(row["seeAlso"]):
                for i in str(row["seeAlso"]).split("|"):
                    seeAlso = URIRef(i.strip())
                    g.add ((concept, RDFS.seeAlso, seeAlso))
            else:
                seeAlso = Literal(row["seeAlso"])
                g.add ((concept, RDFS.seeAlso, seeAlso))
        if not pd.isnull(row["source"]):
            if "|" in str(row["source"]):
                for i in str(row["source"]).split("|"):
                    g.add ((concept, DC.source, Literal(i.strip())))
            else:
                g.add ((concept, DC.source, Literal(row["source"])))
        if not pd.isnull(row["description"]):
            g.add ((concept, SKOS.definition, Literal(row['description'] + languageLabel)))
        if not pd.isnull(row['parent']) and not row["parent"] == "top" :
            broader = URIRef(thesaurusAddendum + row['parent'])
            g.add ((concept, SKOS.broader, broader))
        if not pd.isnull(row['related']):
            if "|" in str(row["related"]):
                for i in str(row["related"]).split("|"):
                    related = URIRef(thesaurusAddendum + i.strip())
                    g.add ((concept, SKOS.related, related))
            else:
                related = URIRef(thesaurusAddendum + row["related"])
                g.add ((concept, SKOS.related, related))
        if not pd.isnull(row['example']):
            if "|" in str(row["example"]):
                for i in str(row["example"]).split("|"):
                    example = Literal(i.strip())
                    g.add ((concept, SKOS.example, example + languageLabel))
            else:
                example = Literal(row["example"])
                g.add ((concept, SKOS.example, example + languageLabel))
        if not pd.isnull(row['relatedMatch']):
            if "|" in str(row["relatedMatch"]):
                for i in str(row["relatedMatch"]).split("|"):
                    relatedMatch = URIRef(i.strip())
                    g.add ((concept, SKOS.relatedMatch, relatedMatch))
            else:
                relatedMatch = URIRef(row["relatedMatch"])
                g.add ((concept, SKOS.relatedMatch, relatedMatch))
        if not pd.isnull(row['closeMatch']):
            if "|" in str(row["closeMatch"]):
                for i in str(row["closeMatch"]).split("|"):
                    closeMatch = URIRef(i.strip())
                    g.add ((concept, SKOS.closeMatch, closeMatch))
            else:
                closeMatch = URIRef(row["closeMatch"])
                g.add ((concept, SKOS.closeMatch, closeMatch))
        g.add ((concept, SKOS.inScheme, thesaurus))
        if row["parent"] == "top":
            g.add ((thesaurus, SKOS.hasTopConcept, concept))
            g.add ((concept, SKOS.topConceptOf, thesaurus))
#g.serialize(destination='fixedData.rdf', format='xml')
g.serialize(destination='fixedData.ttl', format='turtle')
with open('fixedData.ttl', 'r', encoding="utf-8") as f:
    text = f.read()
    text = text.replace('@de"', '"@de')
    text = text.replace("@de>", '>@de')
    #print(text)
with open('fixedData.ttl', 'w', encoding="utf-8") as f:
    f.write(text)