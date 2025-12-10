import json
import os
import networkx as nx
import community as community_louvain
import matplotlib.pyplot as plt
import random

# --- CONFIGURAÇÃO LEVE (PARA VER O RESULTADO RÁPIDO) ---
MIN_MUSICAS = 20
ARQUIVOS_PARA_LER = 10 # Poucos arquivos para o Louvain rodar rápido
NOS_PARA_DESENHAR = 300 # Limite visual para não virar uma "bola de pelos"

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:ARQUIVOS_PARA_LER]

print("--- VISUALIZADOR DE COMUNIDADES (LOUVAIN) ---")
print("1. Montando o grafo (Miniatura)...")

G = nx.Graph()
for nome_arq in arquivos:
    with open(os.path.join(pasta_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_MUSICAS:
                pid = f"P_{pl['pid']}" # Encurtei o nome para o desenho
                tracks = [t['track_name'] for t in pl['tracks']]
                
                # Adiciona nós
                G.add_node(pid, type='playlist')
                for m in tracks:
                    G.add_node(m, type='music')
                    G.add_edge(pid, m)

print(f"Grafo montado com {G.number_of_nodes()} nós.")
print("2. Detectando tribos (Calculando Louvain)...")

# Roda o Louvain no grafo inteiro para achar as cores certas
particao = community_louvain.best_partition(G)
# particao é um dicionário: {'Nome_Do_No': Numero_da_Cor}

# Conta quantas tribos achamos
num_comunidades = len(set(particao.values()))
print(f"-> Encontramos {num_comunidades} tribos diferentes!")

print("3. Preparando a pintura (Selecionando amostra)...")

# Para o desenho ficar bonito, vamos pegar os nós mais conectados (Hubs)
# Se pegarmos nós aleatórios, eles podem ficar soltos na tela.
graus = dict(G.degree())
# Pega os Top nós mais conectados para desenhar
nos_importantes = sorted(graus, key=graus.get, reverse=True)[:NOS_PARA_DESENHAR]

# Cria um sub-grafo só com essa galera VIP
subgrafo = G.subgraph(nos_importantes)

# Pega as cores dessa galera
cores = [particao.get(node) for node in subgrafo.nodes()]

print("4. Desenhando (Uma janela vai abrir)...")

plt.figure(figsize=(12, 12)) # Tamanho da imagem
plt.title(f"Visualização das Comunidades Musicais (Top {NOS_PARA_DESENHAR} Nós)", fontsize=15)

# Layout de Mola (tenta separar os grupos visualmente)
pos = nx.spring_layout(subgrafo, k=0.15, iterations=50)

# Desenha os nós pintados pelas comunidades
nx.draw_networkx_nodes(subgrafo, pos, 
                       node_size=50, 
                       cmap=plt.cm.jet, # Paleta de cores (Arco-íris)
                       node_color=cores, 
                       alpha=0.8)

# Desenha as linhas (arestas) bem fininhas
nx.draw_networkx_edges(subgrafo, pos, alpha=0.1)

# (Opcional) Coloca nome nos nós muito grandes
for node, (x, y) in pos.items():
    # Só escreve o nome se o nó for muito conectado (pra não poluir)
    if graus[node] > 30: # Ajuste esse número se quiser mais/menos nomes
        plt.text(x, y+0.02, s=node, fontsize=8, horizontalalignment='center')

plt.axis('off') # Tira a borda quadrada
plt.show()