import json
import os
import networkx as nx
import community as community_louvain
import math
import random
import numpy as np

# --- CONFIGURAÇÃO ---
ARQUIVOS = 20      # Menos arquivos para teste rápido
QTD_TESTE = 50     # Playlists para testar
BONUS = 0.5        # Peso do Louvain

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS]

print(f"--- 02. VALIDAÇÃO DO MODELO (HÍBRIDO) ---")

# 1. Carregar e Separar
todas = []
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        for pl in json.load(f)['playlists']:
            if len(pl['tracks']) >= 30:
                todas.append((f"P_{pl['pid']}", [t['track_name'] for t in pl['tracks']]))

random.shuffle(todas)
treino = todas[QTD_TESTE:]
teste = todas[:QTD_TESTE]

print(f"Treino: {len(treino)} | Teste: {len(teste)}")

# 2. Grafo de Treino + Teste Parcial
G = nx.Graph()
for pid, tracks in treino:
    G.add_node(pid, type='P')
    for m in tracks: G.add_edge(pid, m)

gabaritos = {}
visiveis_map = {}

for pid, tracks in teste:
    corte = int(len(tracks) * 0.7)
    vis = tracks[:corte]
    escondidas = set(tracks[corte:])
    gabaritos[pid] = escondidas
    visiveis_map[pid] = vis
    G.add_node(pid, type='P')
    for m in vis: G.add_edge(pid, m)

# 3. Louvain
print("Rodando Louvain (aguarde)...")
partition = community_louvain.best_partition(G)

# 4. Avaliação
recalls = []
precisoes = []

for pid, alvo in gabaritos.items():
    vis = visiveis_map[pid]
    tribo_alvo = partition.get(pid, -1)
    candidatos = {}
    
    for m_ponte in vis:
        if m_ponte not in G: continue
        vizinhos = list(G.neighbors(m_ponte))
        peso = 1.0 / (math.log(len(vizinhos) + 1) + 0.1)
        
        for outra_pl in vizinhos:
            if outra_pl == pid: continue
            sugestoes = list(G.neighbors(outra_pl))
            if len(sugestoes) > 100: sugestoes = random.sample(sugestoes, 100)
            
            for sug in sugestoes:
                if sug not in vis:
                    score = peso
                    if partition.get(sug) == tribo_alvo: score += BONUS
                    candidatos[sug] = candidatos.get(sug, 0) + score
    
    top_n = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:len(alvo)*2]
    rec = {x[0] for x in top_n}
    
    acertos = len(rec.intersection(alvo))
    recalls.append(acertos/len(alvo) if len(alvo)>0 else 0)
    precisoes.append(acertos/len(rec) if len(rec)>0 else 0)

print(f"\nRESULTADOS FINAIS:")
print(f"Precision: {np.mean(precisoes)*100:.2f}%")
print(f"Recall:    {np.mean(recalls)*100:.2f}% (Use este número no artigo!)")