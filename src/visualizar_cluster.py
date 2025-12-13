import json
import os
import networkx as nx
import community as community_louvain
from collections import Counter
from datasketch import MinHash, MinHashLSH

# Configuracao
ARQUIVOS = 20           # Número limite de arquivos
MIN_MUSICAS_PL = 50     # Número mínimo de músicas por playlist
LIMIAR_PLAYLISTS = 20   # Número mínimo de playlists por música
TOP_CLUSTERS = 6        # Número de clusters para serem gerados

pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta) if f.endswith(".json")])[:ARQUIVOS]

print("Lendo dados...")
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
print(f"Musicas fortes: {len(musicas_validas)}")

# Criar grafo bipartido
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

print(f"Bipartido reduzido: {B.number_of_nodes()} nos")

# Encontra pares de musicas similares usando LSH
print("Aplicando LSH...")
musicas = [n for n, d in B.nodes(data=True) if d["type"] == "music"]
playlists = [n for n, d in B.nodes(data=True) if d["type"] == "playlist"]

lsh = MinHashLSH(num_perm=128, threshold=0.5)
minhashes = {}

for musica in musicas:
    neighbors = set(B.neighbors(musica))
    mh = MinHash(num_perm=128)
    for neighbor in neighbors:
        mh.update(neighbor.encode('utf8'))
    minhashes[musica] = mh
    lsh.insert(musica, mh)

similar_pairs = set()
musicas_similares = {}
for musica in musicas:
    query_result = lsh.query(minhashes[musica])
    musicas_similares[musica] = [m for m in query_result if m != musica]
    for similar_musica in query_result:
        if musica != similar_musica:
            pair = tuple(sorted([musica, similar_musica]))
            if pair not in similar_pairs:
                similar_pairs.add(pair)

print(f"LSH encontrou {len(similar_pairs)} pares similares")

# Criar grafo bipartido filtrado (apenas arestas para musicas similares)
G_bipartido = nx.Graph()

G_bipartido.add_nodes_from(musicas, type="music")
G_bipartido.add_nodes_from(playlists, type="playlist")

for musica in musicas:
    if musica in musicas_similares and musicas_similares[musica]:
        neighbors = set(B.neighbors(musica))
        for pl in neighbors:
            G_bipartido.add_edge(musica, pl)

print(f"Bipartido filtrado: {G_bipartido.number_of_nodes()} nos, {G_bipartido.number_of_edges()} arestas")

# Louvain
print("Detectando comunidades...")
part = community_louvain.best_partition(G_bipartido)
clusters = Counter(part.values())
maiores = [cid for cid, _ in clusters.most_common(TOP_CLUSTERS)]

nos_final = [n for n in G_bipartido.nodes() if part[n] in maiores]
G_final = G_bipartido.subgraph(nos_final).copy()
print(f"Grafo final: {G_final.number_of_nodes()} nos, {G_final.number_of_edges()} arestas")


for n in G_final.nodes():
    G_final.nodes[n]["label"] = n
    G_final.nodes[n]["modularity_class"] = part[n]

nx.write_gexf(G_final, "clusters_otimizado.gexf")
print("Exportado: clusters_otimizado.gexf")