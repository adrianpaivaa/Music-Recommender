import json
import os
import networkx as nx
import community as community_louvain
import math

# --- CONFIGURAÇÃO ---
MAX_ARQUIVOS = 50       # Ler o suficiente para ter dados, mas não tudo
LIMITE_NOS_VISUAIS = 5000 # O Gephi roda liso com 5k-10k nós. Mais que isso vira bagunça.

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:MAX_ARQUIVOS]

print(f"--- GERADOR DE ARQUIVO GEPHI (.GEXF) ---")
print("1. Montando Grafo (Poda: Playlists>=20, Músicas>=20)...")

# Grafo Temporário
G_raw = nx.Graph()

for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < 20: continue
            
            pid = f"P_{pl['pid']}" # Prefixo P para Playlist
            tracks = [t['track_name'] for t in pl['tracks']]
            
            # Adiciona nós e arestas
            for m in tracks:
                G_raw.add_edge(pid, m) # O NetworkX adiciona os nós automaticamente

print(f"   Grafo Bruto: {G_raw.number_of_nodes()} nós.")

# 2. FILTRAGEM VISUAL (Para ficar bonito no Gephi)
# Vamos manter apenas os nós mais conectados (K-Core ou Top Degree)
# Isso remove o ruído e deixa só a estrutura principal "bonita"
print("2. Filtrando para visualização (Mantendo o 'Core')...")

# Calcula o grau (popularidade) de cada nó
graus = dict(G_raw.degree())
# Ordena e pega os Top X mais conectados
top_nos = sorted(graus, key=graus.get, reverse=True)[:LIMITE_NOS_VISUAIS]

# Cria o subgrafo final
G = G_raw.subgraph(top_nos).copy()

# Remove nós que ficaram isolados depois do corte
G.remove_nodes_from(list(nx.isolates(G)))

print(f"   Grafo Final para Exportação: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")

# 3. DETECÇÃO DE COMUNIDADES (Para colorir)
print("3. Calculando Comunidades (Louvain)...")
partition = community_louvain.best_partition(G)

# Adiciona a informação de comunidade e tamanho dentro de cada nó
for node in G.nodes():
    G.nodes[node]['modularity_class'] = partition[node] # O Gephi usa esse nome pra colorir
    G.nodes[node]['size'] = degrees = G.degree[node]   # O Gephi usa isso pro tamanho da bolinha
    
    # Diferencia Playlist de Música (Opcional, pra pintar diferente se quiser)
    if str(node).startswith("P_"):
        G.nodes[node]['tipo'] = "Playlist"
    else:
        G.nodes[node]['tipo'] = "Musica"

# 4. EXPORTAÇÃO
print("4. Salvando arquivo 'grafo_spotify.gexf'...")
nx.write_gexf(G, "grafo_spotify.gexf")
print("SUCESSO! Agora abra o arquivo 'grafo_spotify.gexf' no Gephi.")