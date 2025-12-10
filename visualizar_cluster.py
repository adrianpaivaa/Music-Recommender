import json
import os
import networkx as nx
import community as community_louvain
from collections import Counter

# ===== CONFIG =====
ARQUIVOS = 40         # reduz MUITO a projeção
MIN_MUSICAS_PL = 50   # playlists mais "fortes"
LIMIAR_PLAYLISTS = 20 # músicas que aparecem em poucas playlists → remover
TOP_CLUSTERS = 6      # clusters para manter

pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta) if f.endswith(".json")])[:ARQUIVOS]

print("\n📦 Lendo dados bons...")
playlist_por_musica = {}
musicas_validas = set()
playlists_validas = []

for nome in arquivos:
    with open(os.path.join(pasta, nome), encoding="utf-8") as f:
        data = json.load(f)
        for pl in data["playlists"]:
            if len(pl["tracks"]) < MIN_MUSICAS_PL: 
                continue
            playlists_validas.append(pl)
            for t in pl["tracks"]:
                uri = t["track_uri"]
                playlist_por_musica.setdefault(uri, 0)
                playlist_por_musica[uri] += 1

musicas_validas = {m for m, c in playlist_por_musica.items() if c >= LIMIAR_PLAYLISTS}
print(f"🔹 músicas fortes: {len(musicas_validas)}")

# ===== Criar bipartido reduzido =====
B = nx.Graph()
for i, pl in enumerate(playlists_validas):
    pid = f"P_{pl['pid']}"
    B.add_node(pid, type="playlist")

    for t in pl["tracks"]:
        uri = t["track_uri"]
        if uri not in musicas_validas: 
            continue
        B.add_node(uri, type="music")
        B.add_edge(pid, uri)

print(f"🔹 bipartido reduzido = {B.number_of_nodes()} nós")

# ===== Projeção item–item =====
print("\n🎧 Projetando...")
musicas = [n for n, d in B.nodes(data=True) if d["type"] == "music"]
G = nx.bipartite.weighted_projected_graph(B, musicas)
print(f"🔹 item–item = {G.number_of_nodes()} nós | {G.number_of_edges()} arestas")

# ===== Louvain =====
print("\n🧩 Clusterizando...")
part = community_louvain.best_partition(G)
clusters = Counter(part.values())
maiores = [cid for cid, _ in clusters.most_common(TOP_CLUSTERS)]
print("📊 Maiores:", clusters.most_common(TOP_CLUSTERS))

nos_final = [n for n in G.nodes() if part[n] in maiores]
G_final = G.subgraph(nos_final).copy()
print(f"\n🎯 Grafo final = {G_final.number_of_nodes()} nós | {G_final.number_of_edges()} arestas")

# ===== Labels para gephi =====
for n in G_final.nodes():
    G_final.nodes[n]["label"] = n
    G_final.nodes[n]["modularity_class"] = part[n]

nx.write_gexf(G_final, "comunidades_globais_otimizado.gexf")
print("\n💾 Exportado: comunidades_globais_otimizado.gexf")
print("→ ABRA NO GEPHI e colore por modularity_class 🎨")
