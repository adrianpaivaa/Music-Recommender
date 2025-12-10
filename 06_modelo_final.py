import json
import os
import networkx as nx
import community as community_louvain # A biblioteca do Louvain
import random
import pandas as pd
from collections import Counter
import gc

# --- CONFIGURAÇÃO ---
MIN_MUSICAS_NA_PLAYLIST = 30  
MIN_APARICOES_DA_MUSICA = 35  
MAX_ARQUIVOS = 200 # Vamos testar com 100 primeiro pois Louvain é pesado

pasta_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(caminho_dados) if f.endswith('.json')])[:MAX_ARQUIVOS]

print(f"--- MODELO COM DETECÇÃO DE COMUNIDADES (LOUVAIN) ---")
print("Passo 1: Construindo Grafo...")

# 1. CONSTRUÇÃO DO GRAFO
contador_musicas = Counter()
for nome_arq in arquivos:
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_MUSICAS_NA_PLAYLIST:
                contador_musicas.update([t['track_name'] for t in pl['tracks']])
    gc.collect()

musicas_validas = {m for m, qtd in contador_musicas.items() if qtd >= MIN_APARICOES_DA_MUSICA}
del contador_musicas
gc.collect()

G = nx.Graph()
teste_set = {} 

for nome_arq in arquivos:
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < MIN_MUSICAS_NA_PLAYLIST: continue
            tracks = [t['track_name'] for t in pl['tracks'] if t['track_name'] in musicas_validas]
            if len(tracks) < 10: continue
            
            pid = f"Playlist_{pl['pid']}"
            random.shuffle(tracks)
            corte = int(len(tracks) * 0.8)
            
            m_treino = tracks[:corte]
            m_teste = tracks[corte:]
            
            if m_teste:
                teste_set[pid] = set(m_teste)
                G.add_node(pid, type='playlist')
                for m in m_treino:
                    G.add_node(m, type='music')
                    G.add_edge(pid, m)
    gc.collect()

print(f"Grafo montado ({G.number_of_nodes()} nós).")
print("Passo 2: Rodando algoritmo de Louvain (Isso pode demorar uns minutos)...")

# 2. APLICANDO LOUVAIN
# Isso retorna um dicionário: { 'Nome_Do_No': Numero_da_Comunidade }
particao = community_louvain.best_partition(G)

qtd_comunidades = len(set(particao.values()))
print(f"Louvain detectou {qtd_comunidades} comunidades (tribos) diferentes no seu grafo!")

# 3. RECOMENDAÇÃO COM BOOST DE COMUNIDADE
def recomendar_louvain(playlist_alvo, k=10):
    if playlist_alvo not in G: return []
    
    # Descobre qual é a tribo dessa playlist
    tribo_alvo = particao.get(playlist_alvo)
    
    vizinhos = list(G.neighbors(playlist_alvo))
    candidatos = {}
    
    for musica_ponte in vizinhos:
        playlists_conectadas = list(G.neighbors(musica_ponte))
        if len(playlists_conectadas) > 100: 
            playlists_conectadas = random.sample(playlists_conectadas, 100)
            
        for vizinha in playlists_conectadas:
            if vizinha == playlist_alvo: continue
            
            musicas_alvo = list(G.neighbors(vizinha))
            if len(musicas_alvo) > 50: musicas_alvo = random.sample(musicas_alvo, 50)

            for nova_musica in musicas_alvo:
                if nova_musica not in vizinhos:
                    score = 1
                    
                    # --- A MÁGICA DO LOUVAIN ---
                    # Se a música recomendada pertencer à MESMA TRIBO da playlist original,
                    # damos um bônus enorme para ela.
                    tribo_musica = particao.get(nova_musica)
                    
                    if tribo_musica == tribo_alvo:
                        score += 0.5 # Bônus de 50% por ser da mesma comunidade
                    
                    candidatos[nova_musica] = candidatos.get(nova_musica, 0) + score
    
    return sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:k]

# 4. AVALIAÇÃO
print("\nAvaliando amostra de 200 playlists...")
amostra = list(teste_set.keys())[:200]
resultados = []

for i, pid in enumerate(amostra):
    if i % 20 == 0: print(f"Processando {i}...")
    
    rec = [x[0] for x in recomendar_louvain(pid)]
    escondidas = teste_set[pid]
    
    acertos = len(set(rec) & escondidas)
    prec = acertos / len(rec) if rec else 0
    rec_val = acertos / len(escondidas) if escondidas else 0
    resultados.append({'Precision': prec, 'Recall': rec_val})

df = pd.DataFrame(resultados)
print("="*40)
print("RESULTADO COM LOUVAIN")
print(f"Precision: {df['Precision'].mean():.4f}")
print(f"Recall:    {df['Recall'].mean():.4f}")
print("="*40)