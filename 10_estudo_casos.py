import json
import os
import networkx as nx
import math
from collections import Counter

# --- CONFIGURAÇÃO ---
MIN_MUSICAS = 20
ARQUIVOS_PARA_LER = 50 # Ler bastante para achar a música que você quer
MUSICA_ALVO = "Bohemian Rhapsody" # <--- DIGITE AQUI A MÚSICA QUE VOCÊ QUER INVESTIGAR
# Sugestões: "Smells Like Teen Spirit", "Despacito", "Shape of You", "Lose Yourself"

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print(f"--- ESTUDO DE CASO ESPECÍFICO: '{MUSICA_ALVO}' ---")
print("1. Procurando a música e montando o grafo...")

G = nx.Graph()
playlist_cobaia_id = None
playlist_cobaia_tracks = []

# 1. Monta grafo e procura a playlist ideal
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < MIN_MUSICAS: continue
            
            pid = f"Playlist_{pl['pid']}"
            tracks = [t['track_name'] for t in pl['tracks']]
            
            # Adiciona ao grafo
            G.add_node(pid, type='playlist')
            for m in tracks:
                G.add_node(m, type='music')
                G.add_edge(pid, m)
            
            # Verifica se essa playlist tem a nossa música alvo
            # E se ainda não escolhemos uma cobaia
            if playlist_cobaia_id is None and MUSICA_ALVO in tracks:
                playlist_cobaia_id = pid
                playlist_cobaia_tracks = tracks
                print(f"-> ENCONTRADA! Usaremos a playlist '{pl['name']}' (ID: {pl['pid']}) como estudo de caso.")

if playlist_cobaia_id is None:
    print(f"ERRO: Não encontrei nenhuma playlist com '{MUSICA_ALVO}' nos arquivos lidos.")
    print("Tente aumentar ARQUIVOS_PARA_LER ou trocar o nome da música.")
    exit()

print("2. Gerando recomendações para essa playlist...")

# Função de Recomendação (IIF)
def recomendar_iif(playlist_alvo):
    vizinhos = list(G.neighbors(playlist_alvo))
    candidatos = {}
    
    for musica_ponte in vizinhos:
        playlists_conectadas = list(G.neighbors(musica_ponte))
        # Peso IIF
        peso = 1.0 / (math.log(len(playlists_conectadas) + 1) + 0.01)
        
        for vizinha in playlists_conectadas:
            if vizinha == playlist_alvo: continue
            musicas_alvo = list(G.neighbors(vizinha))
            
            for nova in musicas_alvo:
                if nova not in vizinhos: # Só recomenda o que ele NÃO tem
                    candidatos[nova] = candidatos.get(nova, 0) + peso
                    
    return sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:15]

recomendacoes = recomendar_iif(playlist_cobaia_id)

# 3. RELATÓRIO DO CASO
print("\n" + "="*60)
print(f"ESTUDO DE CASO: O EFEITO '{MUSICA_ALVO}'")
print("="*60)
print(f"CONTEXTO (O que essa playlist já tinha):")
print(f"- {MUSICA_ALVO} (Âncora)")
# Mostra outras 5 músicas aleatórias da playlist pra dar contexto
outras = [m for m in playlist_cobaia_tracks if m != MUSICA_ALVO][:5]
for m in outras:
    print(f"- {m}")
print(f"(... e mais {len(playlist_cobaia_tracks)-6} músicas)")

print("\nRESULTADO (O que o algoritmo sugeriu):")
for i, (musica, score) in enumerate(recomendacoes):
    print(f"{i+1}. {musica} (Score: {score:.4f})")
print("="*60)