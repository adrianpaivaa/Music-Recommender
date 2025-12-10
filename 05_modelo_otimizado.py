import json
import os
import networkx as nx
import random
import pandas as pd
from collections import Counter

# --- CONFIGURAÇÃO ---
MIN_MUSICAS_NA_PLAYLIST = 20  # O "Facão" nas playlists (Artigo usou 20)
MIN_APARICOES_DA_MUSICA = 5   # O "Facão" nas músicas (Remove as muito raras)
NUM_ARQUIVOS_PARA_LER = 5     # Vamos ler 5 arquivos para ter mais dados!

pasta_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')
arquivos = [f for f in os.listdir(caminho_dados) if f.endswith('.json')][:NUM_ARQUIVOS_PARA_LER]

print(f"--- INICIANDO MODELO OTIMIZADO (O FACÃO) ---")
print(f"Lendo {len(arquivos)} arquivos de dados.")
print(f"Critérios: Playlists >= {MIN_MUSICAS_NA_PLAYLIST} músicas | Músicas >= {MIN_APARICOES_DA_MUSICA} aparições")

# --- PASSO 1: O CENSO (Contar popularidade das músicas) ---
print("\nPasso 1: Contando popularidade das músicas (Isso é rápido)...")
contador_musicas = Counter()

for nome_arq in arquivos:
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for playlist in data['playlists']:
            # Só conta músicas de playlists que já passariam no filtro de tamanho
            if len(playlist['tracks']) >= MIN_MUSICAS_NA_PLAYLIST:
                tracks = [t['track_name'] for t in playlist['tracks']]
                contador_musicas.update(tracks)

# Define quais músicas são "VIPS" (passaram no teste de popularidade)
musicas_validas = {m for m, qtd in contador_musicas.items() if qtd >= MIN_APARICOES_DA_MUSICA}
print(f"Total de músicas únicas encontradas: {len(contador_musicas)}")
print(f"Músicas mantidas após o corte: {len(musicas_validas)} (Removemos as raras)")

# --- PASSO 2: CONSTRUÇÃO DO GRAFO FILTRADO ---
print("\nPasso 2: Construindo Grafo com dados filtrados...")
G_treino = nx.Graph()
teste_set = {} 

for nome_arq in arquivos:
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        
        for playlist in data['playlists']:
            # Filtro 1: Playlist muito curta? Tchau.
            if len(playlist['tracks']) < MIN_MUSICAS_NA_PLAYLIST:
                continue
            
            pid = f"Playlist_{playlist['pid']}"
            
            # Filtro 2: Pega só as músicas que são populares (VIPS)
            tracks_validas = [t['track_name'] for t in playlist['tracks'] if t['track_name'] in musicas_validas]
            
            # Se depois de filtrar as músicas raras, a playlist ficar vazia ou muito pequena, ignora
            if len(tracks_validas) < 10:
                continue
                
            # DIVISÃO TREINO / TESTE (Só nas playlists válidas)
            random.shuffle(tracks_validas)
            ponto_corte = int(len(tracks_validas) * 0.8)
            
            musicas_treino = tracks_validas[:ponto_corte]
            musicas_teste = tracks_validas[ponto_corte:]
            
            if len(musicas_teste) > 0:
                teste_set[pid] = set(musicas_teste)
                
                # Adiciona ao grafo
                G_treino.add_node(pid, type='playlist')
                for musica in musicas_treino:
                    G_treino.add_node(musica, type='music')
                    G_treino.add_edge(pid, musica)

print(f"Grafo montado: {G_treino.number_of_nodes()} nós e {G_treino.number_of_edges()} arestas.")
print(f"Playlists prontas para avaliação: {len(teste_set)}")

# --- PASSO 3: AVALIAÇÃO (Igual ao anterior) ---
print("\nPasso 3: Rodando avaliação (Isso pode demorar um pouco mais)...")

def gerar_top_recomendacoes(grafo, playlist_alvo, k=10):
    if playlist_alvo not in grafo: return []
    musicas_conhecidas = set(grafo.neighbors(playlist_alvo))
    candidatos = {}
    
    # Otimização: Se a playlist tiver MUITOS vizinhos, olha só uma amostra para não travar
    # (O artigo menciona problemas de performance com matrizes grandes)
    vizinhos = list(grafo.neighbors(playlist_alvo)) # Músicas da playlist
    
    for musica in vizinhos:
        playlists_vizinhas = list(grafo.neighbors(musica))
        # Se uma música for MUITO popular (ex: está em 1000 playlists), limitamos
        if len(playlists_vizinhas) > 100: 
            playlists_vizinhas = random.sample(playlists_vizinhas, 100)
            
        for vizinha in playlists_vizinhas:
            if vizinha == playlist_alvo: continue
            
            musicas_da_vizinha = grafo.neighbors(vizinha)
            for nova_musica in musicas_da_vizinha:
                if nova_musica not in musicas_conhecidas:
                    candidatos[nova_musica] = candidatos.get(nova_musica, 0) + 1
    
    recomendacoes = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)
    return [m for m, s in recomendacoes[:k]]

resultados = []
# Avalia apenas uma amostra de 200 playlists para ter o resultado rápido agora
# (No trabalho final você pode rodar com todas)
amostra_teste = list(teste_set.keys())[:200]

for i, pid in enumerate(amostra_teste):
    if i % 50 == 0: print(f"Processando {i}/{len(amostra_teste)}...")
    
    musicas_escondidas = teste_set[pid]
    rec = gerar_top_recomendacoes(G_treino, pid, k=10)
    
    acertos = len(set(rec) & musicas_escondidas)
    
    prec = acertos / len(rec) if rec else 0
    rec_metric = acertos / len(musicas_escondidas) if musicas_escondidas else 0
    
    resultados.append({'Precision': prec, 'Recall': rec_metric})

df = pd.DataFrame(resultados)
print("-" * 40)
print("RESULTADOS COM FILTRO (FACÃO)")
print(f"Precision: {df['Precision'].mean():.4f}")
print(f"Recall:    {df['Recall'].mean():.4f}")
print(f"F1 Score:  {2*(df['Precision'].mean()*df['Recall'].mean())/(df['Precision'].mean()+df['Recall'].mean()):.4f}")
print("-" * 40)