import json
import os
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

# --- 1. CARREGAR DADOS (Amostra pequena para não travar) ---
# Vamos usar apenas 1 arquivo para este teste de conceito
pasta_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')

# Pega o primeiro arquivo
arquivo = [f for f in os.listdir(caminho_dados) if f.endswith('.json')][0]
caminho_completo = os.path.join(caminho_dados, arquivo)

print("Carregando dados e construindo o Grafo...")

# --- 2. CONSTRUÇÃO DO GRAFO BIPARTIDO (Seção V do Artigo) ---
# Inicializa um grafo vazio
G = nx.Graph()

with open(caminho_completo, 'r') as f:
    conteudo = json.load(f)
    
    # Vamos limitar a 50 playlists para visualizar e testar rápido
    playlists_para_processar = conteudo['playlists'][:50]
    
    for playlist in playlists_para_processar:
        pid = f"Playlist_{playlist['pid']}" # Nome do nó da Playlist
        
        # Adiciona o nó da Playlist
        G.add_node(pid, type='playlist')
        
        for track in playlist['tracks']:
            music_uri = track['track_name'] # Usando nome para ficar legível
            
            # Adiciona o nó da Música
            G.add_node(music_uri, type='music')
            
            # CRIA A CONEXÃO (Aresta)
            # Isso representa que a playlist "gostou" da música
            G.add_edge(pid, music_uri)

print(f"Grafo criado com {G.number_of_nodes()} nós e {G.number_of_edges()} conexões.")

# --- 3. ALGORITMO DE RECOMENDAÇÃO (Baseado em Caminhos - Seção V-A) ---
# O artigo diz: "Quanto mais caminhos, maior a chance do usuário gostar"
def recomendar_musicas(playlist_alvo):
    print(f"\n--- Gerando recomendações para: {playlist_alvo} ---")
    
    if playlist_alvo not in G:
        print("Playlist não encontrada no grafo.")
        return

    # Músicas que a playlist JÁ tem
    musicas_que_ja_tem = set(G.neighbors(playlist_alvo))
    print(f"Essa playlist já tem {len(musicas_que_ja_tem)} músicas.")

    candidatos = []
    
    # 1. Achar playlists vizinhas (que compartilham músicas)
    # Isso equivale a achar caminhos de comprimento 2 (User -> Song -> Other User)
    for musica in musicas_que_ja_tem:
        playlists_vizinhas = G.neighbors(musica)
        
        for vizinha in playlists_vizinhas:
            if vizinha == playlist_alvo: continue # Pula ela mesma
            
            # 2. Ver o que essas vizinhas ouvem (Caminho de comprimento 3)
            # User -> Song -> Other User -> New Song
            musicas_da_vizinha = G.neighbors(vizinha)
            for nova_musica in musicas_da_vizinha:
                if nova_musica not in musicas_que_ja_tem:
                    candidatos.append(nova_musica)
    
    # Conta quais músicas apareceram mais vezes (mais caminhos levam a ela)
    contagem = Counter(candidatos)
    
    # Mostra o Top 5
    top_5 = contagem.most_common(5)
    
    print("Recomendações (Música, Pontuação de Caminhos):")
    for musica, score in top_5:
        print(f"-> {musica} (Encontrada por {score} caminhos)")

# --- 4. TESTE ---
# Vamos pegar a primeira playlist do grafo para testar
primeira_playlist = f"Playlist_{playlists_para_processar[0]['pid']}"
recomendar_musicas(primeira_playlist)

# --- 5. VISUALIZAÇÃO (Opcional, só funciona bem com poucos dados) ---
# Desenha uma parte pequena do grafo
print("\nDesenhando grafo (pode demorar uns segundos)...")
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.15, iterations=20)
nx.draw(G, pos, node_size=20, alpha=0.5, node_color="blue", with_labels=False)
plt.title("Visualização do Grafo Bipartido (Playlists x Músicas)")
plt.show()