import json
import os
import networkx as nx
import math
from collections import Counter

# Configuração
ARQUIVOS_PARA_LER = 250     # Número de arquivos para leitura (limitado para 250 devido a restrições no Hardware)
MIN_MUSICAS_PLAYLIST = 20   # Tamanho mínimo de uma playlist
LIMIAR_MUSICAS = 5          # Quantidade mínima de vezes que uma música aparece nas playlists

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print("Carregando dados...")

G = nx.Graph()
nomes_para_uri = {}
uri_para_nome = {}

count = 0
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < MIN_MUSICAS_PLAYLIST:
                continue

            pid = f"Playlist_{pl['pid']}"
            G.add_node(pid, type='playlist')

            for track in pl['tracks']:
                uri = track['track_uri']
                nome = track['track_name']
                artista = track['artist_name']
                nome_completo = f"{nome} - {artista}"

                nomes_para_uri[nome_completo.lower()] = (uri, nome_completo)
                uri_para_nome[uri] = nome_completo

                G.add_node(uri, type='music')
                G.add_edge(pid, uri)

    count += 1
    if count % 10 == 0:
        print(f"{count}/{len(arquivos)}")

# Remove musicas raras (Smart Pruning)
musicas_remover = []
for musica in [n for n, d in G.nodes(data=True) if d.get('type') == 'music']:
    if G.degree(musica) < LIMIAR_MUSICAS:
        musicas_remover.append(musica)

G.remove_nodes_from(musicas_remover)

# Remove playlists que ficaram vazias após o corte
playlists_remover = []
for playlist in [n for n, d in G.nodes(data=True) if d.get('type') == 'playlist']:
    if G.degree(playlist) == 0:
        playlists_remover.append(playlist)

G.remove_nodes_from(playlists_remover)

print(f"Grafo pronto. {G.number_of_nodes()} nos carregados.\n")

def buscar_musica(termo):
    resultados = []
    termo = termo.lower()
    for nome_lower, (uri, nome_real) in nomes_para_uri.items():
        if termo in nome_lower:
            resultados.append((uri, nome_real))
            if len(resultados) >= 10:
                break
    return resultados

def recomendar_por_musica(musica_uri):
    # musica alvo -> playlists que contem ela -> outras musicas nessas playlists
    if musica_uri not in G:
        return []

    playlists_vizinhas = list(G.neighbors(musica_uri))
    candidatos = {}

    # Score usando IIF - Penaliza músicas populares
    for playlist in playlists_vizinhas:
        musicas_na_playlist = list(G.neighbors(playlist))
        
        peso_caminho = 1.0 # O peso de penalidade é todo concentrado no IIF do item (m)
        
        for m in musicas_na_playlist:
            if m == musica_uri:
                continue

            # 1. Calcular o IIF da música sugerida (m)
            # O grau do nó 'm' representa sua popularidade (|Vizinhos(m)|).
            grau_m = G.degree(m)
            # Aplicando a fórmula do IIF
            peso_iif_m = 1.0 / (math.log(grau_m + 1) + 0.1)

            # 2. Somar o peso IIF ao score da música
            candidatos[m] = candidatos.get(m, 0) + (peso_caminho * peso_iif_m)

    ranking = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)[:15]
    return [(uri_para_nome[uri], score) for uri, score in ranking]

# --- LOOP CONSOLE ---
while True:
    print("\n" + "-"*60)
    termo = input("Digite o nome de uma musica (ou 'sair'): ").strip()

    if termo.lower() in ['sair', 'exit', 'quit']:
        break

    resultados = buscar_musica(termo)

    if not resultados:
        print("Música não encontrada.")
        continue

    print("\nEncontrei estas músicas:")
    for i, (uri, nome) in enumerate(resultados):
        print(f"[{i+1}] {nome}")

    escolha = input("\nConfirme sua música (Digite o numero, ou 0 para cancelar): ")

    if not escolha.isdigit():
        continue
    idx = int(escolha) - 1

    if 0 <= idx < len(resultados):
        uri_alvo, nome_alvo = resultados[idx]
        print(f"\nGerando recomendacoes para: {nome_alvo}")

        recs = recomendar_por_musica(uri_alvo)

        if recs:
            print("\nQUEM OUVE ISSO TAMBÉM OUVE:")
            for i, (nome_rec, score) in enumerate(recs):
                print(f"    {i+1}. {nome_rec} ({score:.2f})")
        else:
            print("Nenhuma recomendação disponível.")
    else:
        print("Cancelado.")