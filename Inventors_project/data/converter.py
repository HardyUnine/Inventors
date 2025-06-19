import pandas as pd

# Charger ton CSV contenant inventeurs et inventions
df = pd.read_csv("inventors_inventions.csv")

# Préfixes RDF (standard)
prefixes = """@prefix wdt: <http://www.wikidata.org/prop/direct/> .
@prefix wd: <http://www.wikidata.org/entity/> .

"""

# Créer les triplets RDF pour chaque ligne
triplets = []
for _, row in df.iterrows():
    inventor = row["inventor"]
    invention = row["invention"]
    triplets.append(f"<{inventor}> wdt:P800 <{invention}> .")

# Assembler tout le fichier TTL
ttl_content = prefixes + "\n".join(triplets)

# Sauvegarder le fichier TTL
with open("data/inventors_graph.ttl", "w", encoding="utf-8") as f:
    f.write(ttl_content)

print("✅ Fichier TTL généré : data/inventors_graph.ttl")
