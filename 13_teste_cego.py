import json
import os
import networkx as nx
import community as community_louvain
import math
import random
import numpy as np
import time

# --- CONFIGURAÇÃO ---
ARQUIVOS_PARA_LER = 20      # Menos arquivos para o Louvain não travar seu PC
QTD_PLAYLISTS_TESTE = 50    # Quantas playlists vamos tentar reconstruir
MIN_TAMANHO = 30            # Tamanho mínimo da playlist
BONUS_COMUNIDADE = 0.5      # Quanto ponto extra ganha se for da mesma tribo

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print(f"--- TESTE CEGO AVANÇADO (LOUVAIN + IIF) ---")
print(f"Lendo {ARQUIVOS_PARA_LER} arquivos...")

# 1. CARREGAR E SEPARAR DADOS (TREINO vs TESTE)
todas_playlists = []
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_TAMANHO:
                pid = f"Playlist_{pl['pid']}"
                tracks = [t['track_name'] for t in pl['tracks']]
                todas_playlists.append((pid, tracks))

# Embaralha e separa as vítimas
random.shuffle(todas_playlists)
playlists_teste = todas_playlists[:QTD_PLAYLISTS_TESTE]
playlists_treino = todas_playlists[QTD_PLAYLISTS_TESTE:]

print(f"Total: {len(todas_playlists)} playlists.")
print(f"Usando {len(playlists_treino)} para aprender (Treino) e {len(playlists_teste)} para testar (Vítimas).")

# 2. MONTAR O GRAFO (Sem as músicas escondidas!)
print("\n1. Construindo o Grafo Parcial...")
G = nx.Graph()

# Adiciona playlists de treino completas
for pid, tracks in playlists_treino:
    G.add_node(pid, type='playlist')
    for m in tracks:
        G.add_node(m, type='music')
        G.add_edge(pid, m)

# Adiciona playlists de teste PARCIAIS (só 70%)
gabaritos = {} # Aqui guardamos o que foi escondido
visiveis_map = {} # Aqui guardamos o que o grafo sabe

for pid, tracks in playlists_teste:
    corte = int(len(tracks) * 0.7)
    parte_visivel = tracks[:corte]
    parte_escondida = set(tracks[corte:])
    
    gabaritos[pid] = parte_escondida
    visiveis_map[pid] = set(parte_visivel)
    
    G.add_node(pid, type='playlist')
    for m in parte_visivel:
        G.add_node(m, type='music')
        G.add_edge(pid, m)

print(f"Grafo Montado: {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")

# 3. RODAR LOUVAIN (Detectar Comunidades)
print("\n2. Executando Algoritmo de Louvain (Aguarde...)...")
start_time = time.time()
partition = community_louvain.best_partition(G)
end_time = time.time()
print(f"Louvain concluído em {end_time - start_time:.2f} segundos.")
print(f"Comunidades detectadas: {len(set(partition.values()))}")

# 4. RECOMENDAÇÃO E AVALIAÇÃO
print("\n3. Iniciando Teste de Reconstrução...")
precisoes = []
recalls = []

for i, (pid, escondidas) in enumerate(gabaritos.items()):
    visiveis = visiveis_map[pid]
    
    # Descobre a tribo dessa playlist (baseado no que sobrou dela)
    # Se a playlist ficou isolada (raro), assume tribo -1
    tribo_alvo = partition.get(pid, -1)
    
    candidatos = {}
    
    # Algoritmo IIF
    for musica_ponte in visiveis:
        if musica_ponte not in G: continue
        
        vizinhos = list(G.neighbors(musica_ponte))
        if not vizinhos: continue
            
        peso_iif = 1.0 / (math.log(len(vizinhos) + 1) + 0.1)
        
        for outra_pl in vizinhos:
            if outra_pl == pid: continue
            
            sugestoes = list(G.neighbors(outra_pl))
            # Otimização: se a playlist for muito grande, pega uma amostra pra não demorar
            if len(sugestoes) > 100: sugestoes = random.sample(sugestoes, 100)
            
            for sug in sugestoes:
                if sug not in visiveis:
                    score = peso_iif
                    
                    # --- AQUI ENTRA O LOUVAIN ---
                    tribo_sugestao = partition.get(sug, -2)
                    if tribo_sugestao == tribo_alvo:
                        score += BONUS_COMUNIDADE # Bônus!
                    
                    candidatos[sug] = candidatos.get(sug, 0) + score

    # Top N
    k = len(escondidas) * 2 # Recomendamos o dobro do que escondemos pra dar chance
    ranking = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:k]
    recomendadas = {m[0] for m in ranking}
    
    # Métricas
    acertos = len(recomendadas.intersection(escondidas))
    prec = acertos / len(recomendadas) if len(recomendadas) > 0 else 0
    rec = acertos / len(escondidas) if len(escondidas) > 0 else 0
    
    precisoes.append(prec)
    recalls.append(rec)
    
    if i % 10 == 0: print(f"   Processado {i}/{QTD_PLAYLISTS_TESTE}... (Acertos na última: {acertos})")

# 5. RESULTADO FINAL
media_prec = np.mean(precisoes) * 100
media_rec = np.mean(recalls) * 100

print("\n" + "="*50)
print(f"RESULTADO FINAL COM LOUVAIN (Bônus {BONUS_COMUNIDADE})")
print(f"Precision: {media_prec:.2f}%")
print(f"Recall:    {media_rec:.2f}%")
print("="*50)