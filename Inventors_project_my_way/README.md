# Projet d’analyse des inventeurs

Ce dépôt présente un projet d’exploration et d’analyse de données issues de Wikidata, centré sur la thématique des **inventeurs**. L’objectif est de montrer les différentes étapes de la production et de l’analyse d’informations sous forme de données RDF : extraction via SPARQL, stockage dans un triplestore (AllegroGraph Cloud), traitement statistique et visualisation.

Le workflow se décline en quatre questions de recherche :
- **Q1** : étude de l’évolution de la proportion d’inventrices au fil des décennies.  
- **Q2** : mise en évidence d’une dépendance entre le genre et le siècle de naissance des inventeurs (test du Chi²).  
- **Q3** : (non présenté ici) — analyse bivariée possible entre genre et nationalité.  
- **Q4** : détection des communautés de co-inventeurs à partir d’un graphe RDF projeté.

Chaque section correspond à un notebook Jupyter détaillé, accompagné des scripts d’extraction, de transformation et de visualisation. Les données RDF sont stockées dans AllegroGraph et mises à disposition, exportées au format Turtle compressé pour assurer une traçabilité et une reproductibilité complètes.  

## Q1 – Évolution de la proportion d’inventrices

**Question de recherche :**  
Comment a évolué la proportion d’inventrices (femmes) au fil des décennies ?

### 1. Extraction des données  
Requête SPARQL sur Wikidata pour récupérer les inventeurs avec leur genre et leur date de naissance :  
```sparql
SELECT ?inventor ?genderLabel ?birth WHERE {
  ?inventor wdt:P106 wd:Q205375 ;
            wdt:P31 wd:Q5 ;
            wdt:P21 ?gender ;
            wdt:P569 ?birth .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
}
LIMIT 10000




## Q4 – Analyse de réseau de co-inventeurs

**Question de recherche :**  
Peut-on détecter des communautés d’inventeurs connectés par des co-inventions ?

---

### 1. Construction du graphe RDF  
- Données extraites de Wikidata : triplets `inventor wdt:P800 invention`.  
- Fichier Turtle généré (`inventors_graph.ttl`) et importé dans le repository `inventors` sur AllegroGraph Cloud.  
- Export complet du repository via une requête SPARQL `CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }` et compressé en `data/inventors_graph.ttl.gz`.

### 2. Projection et détection de communautés  
1. Export CSV des relations `inventor → invention` depuis AllegroGraph.  
2. Lecture du CSV dans un notebook Python avec `pandas`.  
3. Construction d’un graphe biparti (inventeurs ↔ inventions) puis projection sur le seul ensemble des inventeurs (`networkx.bipartite.weighted_projected_graph`).  
4. Application de l’algorithme de Louvain (`python-louvain`) pour détecter les communautés.

### 3. Résultats  
- Le réseau projeté forme un **grand composant connexe** (beaucoup d’inventeurs reliés par au moins une invention commune).  
- Plusieurs **communautés majeures** (groupes d’inventeurs fortement interconnectés) et des **petits clusters isolés** (collaborations restreintes ou duos spécialisés) ont été identifiés.  
- Visualisation dans le notebook : chaque nœud coloré selon sa communauté.

### 4. Code et visualisation  
Voir le notebook : `notebooks/04_co_inventors_network.ipynb`  
![Extrait du graphe de co-inventeurs](notebooks/output_co_inventors.png)

---
