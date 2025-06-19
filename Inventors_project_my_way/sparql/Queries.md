# Summary of SPARQL Queries

1. **Basic inventors extraction**  
    ```sparql
       # Liste de 1000 inventeurs avec genre, nationalité et date de naissance
       SELECT ?inventor ?inventorLabel ?countryLabel ?genderLabel ?birth WHERE {
         ?inventor wdt:P106 wd:Q205375 ;
                   wdt:P31 wd:Q5 ;
                   wdt:P27 ?country ;
                   wdt:P21 ?gender ;
                   wdt:P569 ?birth .
         SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
       }
       LIMIT 1000
    ```
*Récupère un échantillon de base d’inventeurs et leurs variables qualitatives pour les analyses Q1–Q3.*

2. **Q1 et Q3 – Genre & date de naissance**  
    ```sparql
       # Inventeurs avec genre et date de naissance
       SELECT ?inventor ?genderLabel ?birth WHERE {
         ?inventor wdt:P106 wd:Q205375 ;
                   wdt:P31 wd:Q5 ;
                   wdt:P21 ?gender ;
                   wdt:P569 ?birth .
         SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
       }
       LIMIT 10000
    ```
*Base pour calculer la proportion d’inventrices par décennie (Q1).*

3. **Q2 (initial) – Genre & nationalité**  
    ```sparql
       # Inventeurs avec genre et pays (optionnel)
       SELECT DISTINCT ?inventor ?genderLabel ?countryLabel WHERE {
         ?inventor wdt:P31 wd:Q205375 .
         OPTIONAL { ?inventor wdt:P21 ?gender . }
         OPTIONAL { ?inventor wdt:P27 ?country . }
         SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
       }
    ```
*Premier essai pour faire le tableau genre × pays (Q2).*

4. **Q2 (robuste) – Genre & nationalité obligatoires**  
    ```sparql
       # Inventeurs filtrés avec genre et pays 
       SELECT DISTINCT ?inventor ?inventorLabel ?genderLabel ?countryLabel WHERE {
         ?inventor wdt:P106 wd:Q205375 ;
                   wdt:P31 wd:Q5 ;
                   wdt:P21 ?gender ;
                   wdt:P27 ?country .
         SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
       }
       LIMIT 5000
    ```
*Extrait un échantillon significatif pour le test du Chi² (Q2).*

5. **Q4 – Inventeur → invention**  
    ```sparql
       # Tous les liens inventeur → oeuvre marquante
       SELECT DISTINCT ?inventor ?invention WHERE {
         ?inventor <http://www.wikidata.org/prop/direct/P800> ?invention .
       }
    ```
*Base du graphe biparti inventeurs ↔ inventions pour Q4.*

6. **Q4 – Co-inventeurs**  
    ```sparql
       # Paires d'inventeurs ayant la même invention
       SELECT DISTINCT ?inv1 ?inv2 WHERE {
         ?inv1 <http://www.wikidata.org/prop/direct/P800> ?invention .
         ?inv2 <http://www.wikidata.org/prop/direct/P800> ?invention .
         FILTER(?inv1 != ?inv2)
       }
    ```
*Génère les arêtes du réseau d’inventeurs pour détection de communautés (Q4).*

7. **Export complet du triplestore**  
    ```sparql
       CONSTRUCT {
         ?s ?p ?o
       } WHERE {
         ?s ?p ?o
       }
    ```
*Exporte tous les triplets RDF au format Turtle.*