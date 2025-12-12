import json
import os
import networkx as nx
import math
from collections import Counter

# --- CONFIGURAÇÃO ---
ARQUIVOS_PARA_LER = 250
MIN_MUSICAS_PLAYLIST = 20

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print("Carregando dados e montando grafo...")

G = nx.Graph()
nomes_para_uri = {} # Dicionário para buscar por nome
uri_para_nome = {}

count = 0
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < MIN_MUSICAS_PLAYLIST: continue
            
            pid = f"Playlist_{pl['pid']}"
            
            # Adiciona playlist ao grafo
            G.add_node(pid, type='playlist')
            
            for track in pl['tracks']:
                uri = track['track_uri']
                nome = track['track_name']
                artista = track['artist_name']
                nome_completo = f"{nome} - {artista}"
                
                # Guarda mapeamento para busca
                nomes_para_uri[nome_completo.lower()] = (uri, nome_completo)
                uri_para_nome[uri] = nome_completo
                
                # Adiciona nó de música e aresta
                G.add_node(uri, type='music')
                G.add_edge(pid, uri)
    
    count += 1
    if count % 10 == 0: print(f"Processados {count}/{len(arquivos)} arquivos...")

# --- MÉTRICAS ANTES DO SMART PRUNING ---
print("\n📊 CALCULANDO MÉTRICAS ANTES DO SMART PRUNING...")
nós_antes = G.number_of_nodes()
arestas_antes = G.number_of_edges()
grau_medio_antes = sum(dict(G.degree()).values()) / nós_antes if nós_antes > 0 else 0

# --- SMART PRUNING ---
print("\n🔪 APLICANDO SMART PRUNING...")

# Remove músicas que aparecem em muito poucas playlists
LIMIAR_MUSICAS = 2  # Mínimo de playlists por música
musicas_remover = []
for musica in [n for n, d in G.nodes(data=True) if d.get('type') == 'music']:
    grau = G.degree(musica)
    if grau < LIMIAR_MUSICAS:
        musicas_remover.append(musica)

G.remove_nodes_from(musicas_remover)
print(f"   Removidas {len(musicas_remover)} músicas com grau < {LIMIAR_MUSICAS}")

# Remove playlists que ficaram vazias após remoção
playlists_remover = []
for playlist in [n for n, d in G.nodes(data=True) if d.get('type') == 'playlist']:
    grau = G.degree(playlist)
    if grau == 0:
        playlists_remover.append(playlist)

G.remove_nodes_from(playlists_remover)
print(f"   Removidas {len(playlists_remover)} playlists vazias")

# --- MÉTRICAS DEPOIS DO SMART PRUNING ---
print("\n📊 CALCULANDO MÉTRICAS DEPOIS DO SMART PRUNING...")
nós_depois = G.number_of_nodes()
arestas_depois = G.number_of_edges()
grau_medio_depois = sum(dict(G.degree()).values()) / nós_depois if nós_depois > 0 else 0

# --- TABELA COMPARATIVA ---
print("\n" + "="*70)
print("📈 TABELA COMPARATIVA - SMART PRUNING")
print("="*70)
print(f"{'MÉTRICA':<25} {'ANTES':<20} {'DEPOIS':<20}")
print("-"*70)
print(f"{'Nós (vértices)':<25} {nós_antes:<20} {nós_depois:<20}")
print(f"{'Arestas':<25} {arestas_antes:<20} {arestas_depois:<20}")
print(f"{'Grau Médio':<25} {grau_medio_antes:<20.2f} {grau_medio_depois:<20.2f}")

# Calcula variações
var_nos = ((nós_depois - nós_antes) / nós_antes * 100) if nós_antes > 0 else 0
var_arestas = ((arestas_depois - arestas_antes) / arestas_antes * 100) if arestas_antes > 0 else 0
var_grau = ((grau_medio_depois - grau_medio_antes) / grau_medio_antes * 100) if grau_medio_antes > 0 else 0

print("-"*70)
print(f"{'REDUÇÃO (%)':<25} {var_nos:<20.2f}% {var_arestas:<20.2f}%")
print("="*70 + "\n")

print(f"Grafo pronto. {G.number_of_nodes()} nós carregados.")
print("="*60)

# --- FUNÇÃO DE BUSCA E RECOMENDAÇÃO ---

def buscar_musica(termo):
    resultados = []
    termo = termo.lower()
    for nome_lower, (uri, nome_real) in nomes_para_uri.items():
        if termo in nome_lower:
            resultados.append((uri, nome_real))
            if len(resultados) >= 10: break # Limita a 10 resultados
    return resultados

def recomendar_por_musica(musica_uri):
    # A lógica aqui é Item-Item via Graph:
    # Música Alvo -> Playlists que a contêm -> Outras Músicas nessas playlists
    
    if musica_uri not in G: return []
    
    playlists_vizinhas = list(G.neighbors(musica_uri))
    candidatos = {}
    
    # Heurística IIF
    for playlist in playlists_vizinhas:
        # Peso da playlist (se a playlist for gigante e genérica, vale menos)
        peso_playlist = 1.0 / (math.log(len(list(G.neighbors(playlist))) + 1) + 0.1)
        
        musicas_na_playlist = list(G.neighbors(playlist))
        for m in musicas_na_playlist:
            if m == musica_uri: continue
            
            # Soma o peso
            candidatos[m] = candidatos.get(m, 0) + peso_playlist

    # Ordena e formata
    ranking = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:15]
    return [(uri_para_nome[uri], score) for uri, score in ranking]

# --- LOOP INTERATIVO ---
while True:
    print("\n" + "-"*60)
    termo = input("Digite o nome de uma música (ou 'sair'): ").strip()
    
    if termo.lower() in ['sair', 'exit', 'quit']:
        break
    
    if len(termo) < 2:
        print("Digite pelo menos 2 letras.")
        continue
        
    resultados = buscar_musica(termo)
    
    if not resultados:
        print(" Música não encontrada na base carregada. Tente novamente.")
        continue
    
    print("\nEncontrei estas músicas:")
    for i, (uri, nome) in enumerate(resultados):
        print(f"[{i+1}] {nome}")
    
    escolha = input("\nQual delas é a correta? (Digite o número, ou 0 para cancelar): ")
    
    if not escolha.isdigit(): continue
    idx = int(escolha) - 1
    
    if 0 <= idx < len(resultados):
        uri_alvo, nome_alvo = resultados[idx]
        print(f"\nGerando recomendações baseadas em: '{nome_alvo}'...")
        
        recs = recomendar_por_musica(uri_alvo)
        
        print(f"\nQUEM OUVE ISSO TAMBÉM OUVE:")
        for i, (nome_rec, score) in enumerate(recs):
            print(f"   {i+1}. {nome_rec} (Score: {score:.2f})")
    else:
        print("Cancelado.")