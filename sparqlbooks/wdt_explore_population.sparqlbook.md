## Explore Wikidata

In this notebook, I refine and document the main requests available on the page Exploration of Wikidata, with a particular focus on individuals listed on the List of Inventors from Wikipedia.

### Explore occupations and fields of work among inventors

```sparql
### List 50 most frequent occupations among inventors
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?occupation ?occupationLabel (COUNT(?inventor) as ?inventorCount)
WHERE {
    ?inventor wdt:P31 wd:Q5;
              wdt:P106 wd:Q205375.
              
    OPTIONAL { ?inventor wdt:P106 ?occupation. }
    FILTER(?occupation != wd:Q205375)

    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?occupation ?occupationLabel
ORDER BY DESC(?inventorCount)
LIMIT 50
```

```sparql
### List 20 most frequent fields of work of inventors
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?field ?fieldLabel (COUNT(?inventor) AS ?fieldCount)
WHERE {
  ?inventor wdt:P106 wd:Q205375;
            wdt:P101 ?field.

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?field ?fieldLabel
ORDER BY DESC(?fieldCount)
LIMIT 20
```

```sparql
### Gender distribution among inventors
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?gender ?genderLabel (COUNT(?inventor) AS ?count)
WHERE {
  ?inventor wdt:P106 wd:Q205375;
            wdt:P21 ?gender.

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?gender ?genderLabel
ORDER BY DESC(?count)
```

