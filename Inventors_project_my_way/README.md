# Analyse des Inventeurs – Projet Wikidata & RDF

Ce projet explore les **inventeurs** de Wikidata sous différents angles :  
- Évolution temporelle de la proportion de femmes inventrices  
- Relations entre variables qualitatives (genre, pays, siècle)  
- Structure de réseau de co-invention et détection de communautés  

Les données sont extraites via SPARQL, stockées dans un triplestore (AllegroGraph Cloud), analysées en Python (pandas, scipy, networkx) et documentées dans des notebooks Jupyter.

---

## Q1 – Évolution de la proportion d’inventrices

**Question de recherche :**  
Comment a évolué la proportion d’inventrices (femmes) au fil des décennies ?

### 1. Extraction SPARQL  
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

Export → `data/inventors_gender_birth.csv`

### 2. Traitement & visualisation

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/inventors_gender_birth.csv")
df['birth']   = pd.to_datetime(df['birth'], errors='coerce')
df = df.dropna(subset=['birth'])
df['decade']  = (df['birth'].dt.year // 10) * 10
pivot = df.pivot_table(index='decade', columns='genderLabel', aggfunc='size', fill_value=0)
pivot['total'] = pivot.sum(axis=1)
pivot['prop_femmes'] = pivot.get('féminin', 0) / pivot['total']

pivot['prop_femmes'].plot(marker='o')
plt.title("Proportion d'inventrices par décennie")
plt.xlabel("Décennie")
plt.ylabel("Proportion de femmes")
plt.grid(True)
plt.show()
```

### 3. Résultat

On observe une proportion presque nulle avant 1900, puis une montée progressive depuis le XXᵉ siècle.
*(Voir `notebooks/Query_1.ipynb`)*

---

## Q2 – Genre vs. Nationalité

**Question :**
Existe-t-il une association statistiquement significative entre le **genre** des inventeurs et leur **pays de citoyenneté** ?

### 1. Extraction SPARQL

```sparql
# Inventeurs avec genre et pays obligatoires
SELECT DISTINCT ?inventor ?genderLabel ?countryLabel WHERE {
  ?inventor wdt:P106 wd:Q205375 ;
            wdt:P31 wd:Q5 ;
            wdt:P21 ?gender ;
            wdt:P27 ?country .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
}
LIMIT 5000
```

Export → `data/inventors_gender_country.csv`

### 2. Nettoyage, Chi² & top-10 barplot

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency

df = pd.read_csv("data/inventors_gender_country.csv") \
       .dropna(subset=['countryLabel','genderLabel'])
totaux = df['countryLabel'].value_counts()
top10 = totaux.nlargest(10).index
df['country_top'] = df['countryLabel'].where(df['countryLabel'].isin(top10), 'Autres')

cont = pd.crosstab(df['country_top'], df['genderLabel'])
chi2, p, _, _ = chi2_contingency(cont)
print(f"Chi² = {chi2:.2f}, p-value = {p:.2e}")

plt.figure(figsize=(8,6))
cont.loc[list(top10)+['Autres']].plot(
    kind='barh', stacked=True, width=0.8, ax=plt.gca()
)
plt.title("Répartition par genre – Top 10 pays + Autres")
plt.xlabel("Nombre d'inventeurs")
plt.ylabel("Pays")
plt.legend(title="Genre", bbox_to_anchor=(1,1))
plt.tight_layout()
plt.show()
```

### 3. Résultat

**p-value < 10⁻⁶** : dépendance significative genre × nationalité.
Le top 10 des pays concentre l’essentiel des effectifs, les autres sont regroupés.
*(Voir `notebooks/Query_2.ipynb`)*

---

## Q3 – Genre vs. Siècle de naissance

**Question :**
Le genre des inventeurs varie-t-il selon leur **siècle de naissance** ?

### 1. Extraction SPARQL

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

Export → `data/inventors_gender_birth.csv`

### 2. Traitement & Chi²

```python
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

df = pd.read_csv("data/inventors_gender_birth.csv")
df['birth']   = pd.to_datetime(df['birth'], errors='coerce')
df = df.dropna(subset=['birth','genderLabel'])
df['century'] = (df['birth'].dt.year // 100 + 1).astype(int).astype(str) + "e"

cont = pd.crosstab(df['century'], df['genderLabel'])
chi2, p, _, _ = chi2_contingency(cont)
print(f"Chi² = {chi2:.2f}, p-value = {p:.2e}")

cont.plot(kind='bar', stacked=True)
plt.title("Genres par siècle de naissance")
plt.xlabel("Siècle")
plt.ylabel("Nombre d'inventeurs")
plt.tight_layout()
plt.show()
```

### 3. Résultat

 **p-value ≈ 0** : forte dépendance genre × siècle.

Très peu de femmes avant le XIXᵉ, puis croissance marquée au XXᵉ.
*(Voir `notebooks/Query_3.ipynb`.)*

---

## Q4 – Communautés de co-inventeurs

**Question :**
Peut-on détecter des **communautés** d’inventeurs connectés par des co-inventions ?

### 1. Extraction RDF & import

* Génération de `inventors_graph.ttl` depuis `data/inventors_inventions.csv` (prédicat `wdt:P800`).
* Import dans le repository `inventors` sur AllegroGraph Cloud.
* Export complet → `rdf/results.ttl`.

### 2. Paires de co-inventeurs (SPARQL)

```sparql
SELECT DISTINCT ?inv1 ?inv2 WHERE {
  ?inv1 <http://www.wikidata.org/prop/direct/P800> ?invention .
  ?inv2 <http://www.wikidata.org/prop/direct/P800> ?invention .
  FILTER(?inv1 != ?inv2)
}
```

Export CSV → `data/inventor_pairs.csv`

### 3. Analyse réseau en Python

```python
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import community as community_louvain

pairs = pd.read_csv("data/inventor_pairs.csv")
B = nx.Graph()
B.add_nodes_from(pairs['inv1'], bipartite=0)
B.add_nodes_from(pairs['inv2'], bipartite=1)
B.add_edges_from(pairs[['inv1','inv2']].itertuples(index=False, name=None))

inventors = pairs['inv1'].unique()
G = nx.bipartite.weighted_projected_graph(B, inventors)

partition = community_louvain.best_partition(G)
pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(10,7))
nx.draw_networkx_nodes(
    G, pos,
    node_color=list(partition.values()),
    cmap=plt.cm.Set3,
    node_size=100
)
nx.draw_networkx_edges(G, pos, alpha=0.3)
plt.title("Communautés de co-inventeurs")
plt.axis("off")
plt.show()
```

### 4. Résultat

Un grand composant connexe avec plusieurs **clusters** colorés :
* **Groupes denses** de collaborations
* **Petits duos** ou isolés
*(Voir `notebooks/Query_4.ipynb`.)*

---

## ChatGPT – Scripts d’import RDF via API

Comme l’interface AllegroGraph Cloud ne permettait ni l’import direct de TTL ni un mapping CSV fiable, j’ai utilisé ChatGPT pour générer deux scripts Python permettant d’injecter les triplets RDF dans le triplestore via l’API REST.

### ChatGPT – Script 1 (upload TTL)

```python
import requests

# Configuration
repo = "inventors"  # nom exact du repository (sensible à la casse)
username = "admin"   # ou ton identifiant perso si différent
password = "lufPfX24ZSD08XwvAeQZni"  # remplace par ton mot de passe admin
host = "https://ag1fel0tr8v5dgez.allegrograph.cloud"

# Endpoint RDF
endpoint = f"{host}/repositories/{repo}/statements"

# Lire le fichier TTL
with open("../data/inventors_graph.ttl", "rb") as f:
    rdf_data = f.read()

# Affichage de vérification
print("----- Aperçu du RDF -----")
print(rdf_data.decode('utf-8')[:300])
print("-------------------------")

# Envoi à AllegroGraph
response = requests.post(
    endpoint,
    headers={"Content-Type": "text/turtle"},
    data=rdf_data,
    auth=(username, password)
)

# Résultat
print(f"Status: {response.status_code}")
print(response.text)
```

### ChatGPT – Script 2 (alternatif)

```python
import requests

# 1. Modifier ces variables selon ton instance
repo = "Inventors"  # nom exact du repository, sensible à la casse
username = "admin"
password = "lufPfX24ZSD08XwvAeQZni"
host = "https://ag1fel0tr8v5dgez.allegrograph.cloud/repositories/inventors/"

# 2. Endpoint pour injecter les triplets RDF
endpoint = f"{host}/repositories/{repo}/statements"

# 3. Lire ton fichier TTL
with open("../data/inventors_graph.ttl", "rb") as f:
    rdf_data = f.read()

# 4. Envoi via POST
response = requests.post(
    endpoint,
    headers={"Content-Type": "text/turtle"},
    data=rdf_data,
    auth=(username, password)
)

# 5. Résultat
print(f"Status: {response.status_code}")
print(response.text)
```


## Conclusion

Ce projet a démontré comment :

1. **Extraire** des données de Wikidata via SPARQL.
2. **Stocker** et **interroger** un triplestore RDF (AllegroGraph Cloud).
3. **Analyser** des variables qualitatives (Q1–Q3) et tester des hypothèses statistiques.
4. **Construire** et **visualiser** un réseau collaboratif (Q4) avec détection de communautés.

```
```
