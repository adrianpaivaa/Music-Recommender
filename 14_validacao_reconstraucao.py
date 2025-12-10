import json
import os
import networkx as nx
import math
import random
import numpy as np

# --- CONFIGURAÇÃO ---
ARQUIVOS_PARA_LER = 50
QTD_PLAYLISTS_TESTE = 100  # Vamos testar 100 para ter uma média sólida
MIN_TAMANHO = 30           # Só playlists com carne pra cortar

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print(f"--- VALIDAÇÃO DE RECONSTRUÇÃO ({QTD_PLAYLISTS_TESTE} Playlists) ---")
print("1. Montando Grafo...")

G = nx.Graph()
candidatas = []

for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_TAMANHO:
                pid = f"Playlist_{pl['pid']}"
                tracks = [t['track_name'] for t in pl['tracks']]
                candidatas.append((pid, tracks))
                
                # Adiciona ao grafo
                G.add_node(pid, type='playlist')
                for m in tracks:
                    G.add_node(m, type='music')
                    G.add_edge(pid, m)

# 2. O LOOP DE TESTE
print(f"2. Iniciando bateria de testes em {QTD_PLAYLISTS_TESTE} playlists aleatórias...")
random.shuffle(candidatas)
amostra = candidatas[:QTD_PLAYLISTS_TESTE]

precisoes = []
recalls = []

for i, (pid, musicas) in enumerate(amostra):
    # Separa Treino (70%) e Teste (30%)
    corte = int(len(musicas) * 0.7)
    visiveis = musicas[:corte]
    escondidas = set(musicas[corte:])
    
    # Remove conexões das escondidas (para não trapacear)
    # Nota: Em um teste rápido, podemos apenas ignorar a aresta na contagem, 
    # mas remover é mais garantido. Para ser rápido, vamos simular a remoção:
    # O algoritmo só vai considerar vizinhos das "visiveis".
    
    candidatos_score = {}
    
    for musica_ponte in visiveis:
        if musica_ponte not in G: continue
        
        vizinhos = list(G.neighbors(musica_ponte))
        # IIF
        peso = 1.0 / (math.log(len(vizinhos) + 1) + 0.1)
        
        for outra_pl in vizinhos:
            if outra_pl == pid: continue # Não olha pra si mesmo
            
            # Recomenda o que a outra playlist tem
            for sugestao in G.neighbors(outra_pl):
                if sugestao not in visiveis:
                    candidatos_score[sugestao] = candidatos_score.get(sugestao, 0) + peso
    
    # Top N (Tamanho da lista escondida * 1.5)
    k = len(escondidas)
    ranking = sorted(candidatos_score.items(), key=lambda x: x[1], reverse=True)[:k]
    recomendadas = {m[0] for m in ranking}
    
    # Métricas
    acertos = len(recomendadas.intersection(escondidas))
    
    precisao = acertos / k if k > 0 else 0
    recall = acertos / len(escondidas) if len(escondidas) > 0 else 0
    
    precisoes.append(precisao)
    recalls.append(recall)
    
    if i % 10 == 0: print(f"   Processado {i}/{QTD_PLAYLISTS_TESTE}...")

# 3. RESULTADO FINAL
media_precisao = np.mean(precisoes) * 100
media_recall = np.mean(recalls) * 100

print("\n" + "="*40)
print(f"RESULTADO FINAL ({QTD_PLAYLISTS_TESTE} ARQUIVOS)")
print(f"Precision: {media_precisao:.2f}%")
print(f"Recall:    {media_recall:.2f}%")
print("="*40)