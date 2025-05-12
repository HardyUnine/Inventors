## Explore Wikidata

In this notebook, I explore more relevant data to this prosopographic study on inventors

### Explore occupations and fields of work among inventors

```sparql
SELECT ?inventor ?inventorLabel ?dateOfBirth ?dateOfDeath ?countryLabel ?inventionLabel WHERE {
  ?inventor wdt:P31 wd:Q5.  # is human
  ?inventor wdt:P61 ?invention.  # has invented something
  OPTIONAL { ?inventor wdt:P569 ?dateOfBirth. }
  OPTIONAL { ?inventor wdt:P570 ?dateOfDeath. }
  OPTIONAL { ?inventor wdt:P27 ?country. }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
LIMIT 500
