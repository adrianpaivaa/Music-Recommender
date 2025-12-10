import json
import os
import networkx as nx
import random
import math
from collections import Counter

# --- CONFIGURAÇÃO ---
MIN_MUSICAS = 20
ARQUIVOS_PARA_LER = 20 # Lê poucos só pra montar um grafo rápido

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print("--- MONTANDO O GRAFO PARA A PROVA ---")
G = nx.Graph()
playlists_completas = {} # Guarda a playlist inteira original

# 1. Monta o grafo (sem esconder nada ainda, só pra ter o "mundo")
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_MUSICAS:
                pid = f"Playlist_{pl['pid']}"
                tracks = [t['track_name'] for t in pl['tracks']]
                playlists_completas[pid] = tracks # Guarda original
                
                # Adiciona ao grafo
                G.add_node(pid, type='playlist')
                for m in tracks:
                    G.add_node(m, type='music')
                    G.add_edge(pid, m)

print(f"Grafo montado. Escolhendo uma vítima...")

# 2. Escolhe uma playlist aleatória para ser a "Cobaia"
pid_cobaia = random.choice(list(playlists_completas.keys()))
musicas_originais = playlists_completas[pid_cobaia]

# 3. REALIZA A LOBOTOMIA (Ocultação)
# Aqui provamos que o grafo NÃO SABE a resposta
random.shuffle(musicas_originais)
corte = int(len(musicas_originais) * 0.8)

musicas_visiveis = musicas_originais[:corte] # O que o grafo vê
musicas_escondidas = musicas_originais[corte:] # O que ele tem que adivinhar

# Removemos as arestas das músicas escondidas TEMPORARIAMENTE
# Isso garante que não tem trapaça. O grafo perde a conexão.
for m in musicas_escondidas:
    if G.has_edge(pid_cobaia, m):
        G.remove_edge(pid_cobaia, m)

# 4. RODANDO O ALGORITMO (Versão Ponderada)
print(f"Testando na playlist: {pid_cobaia}")
vizinhos = musicas_visiveis # O algoritmo só pode usar isso
candidatos = {}

for musica_ponte in vizinhos:
    if musica_ponte not in G: continue
    playlists_vizinhas = list(G.neighbors(musica_ponte))
    
    peso = 1.0 / (math.log(len(playlists_vizinhas) + 1) + 0.1)
    
    for vizinha in playlists_vizinhas:
        if vizinha == pid_cobaia: continue
        musicas_alvo = list(G.neighbors(vizinha))
        
        for nova in musicas_alvo:
            if nova not in musicas_visiveis:
                candidatos[nova] = candidatos.get(nova, 0) + peso

ranking = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:10]
top_recomendacoes = [x[0] for x in ranking]

# 5. O VEREDITO (A PROVA)
print(f"\n{'='*50}")
print(f"PROVA REAL DE FUNCIONAMENTO")
print(f"{'='*50}")
print(f"1. MÚSICAS QUE DEIXAMOS ELE VER ({len(musicas_visiveis)}):")
print(f"   {musicas_visiveis[:5]} ...")

print(f"\n2. MÚSICAS QUE ESCONDEMOS DELE (GABARITO):")
print(f"   {musicas_escondidas}")

print(f"\n3. O QUE ELE ADIVINHOU:")
for i, m in enumerate(top_recomendacoes):
    status = "✅ ACHOU!" if m in musicas_escondidas else "❌ Errou"
    print(f"   {i+1}. {m} [{status}]")

print(f"\n{'='*50}")
if any(m in musicas_escondidas for m in top_recomendacoes):
    print("CONCLUSÃO: O ALGORITMO FUNCIONA! Ele encontrou músicas que estavam invisíveis.")
else:
    print("CONCLUSÃO: Ele errou hoje. Tente rodar de novo (é probabilístico).")