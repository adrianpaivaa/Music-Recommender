import json
import os
import networkx as nx
import random
import pandas as pd

# --- 1. CONFIGURAÇÃO ---
pasta_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')
arquivo = [f for f in os.listdir(caminho_dados) if f.endswith('.json')][0]
caminho_completo = os.path.join(caminho_dados, arquivo)

print("--- INICIANDO AVALIAÇÃO DE DESEMPENHO (SEÇÃO VI DO ARTIGO) ---")

# --- 2. PREPARAÇÃO DOS DADOS (TRAIN / TEST SPLIT) ---
# O artigo sugere dividir os dados para testar se o modelo acerta [cite: 220]
print("Carregando dados e dividindo em Treino/Teste...")

G_treino = nx.Graph()
teste_set = {} # Dicionário para guardar as músicas escondidas: {playlist_id: [musicas_escondidas]}

with open(caminho_completo, 'r') as f:
    conteudo = json.load(f)
    # Usaremos 1000 playlists para ter uma amostra estatística relevante
    playlists = conteudo['playlists'][:1000] 
    
    for playlist in playlists:
        pid = f"Playlist_{playlist['pid']}"
        tracks = [t['track_name'] for t in playlist['tracks']]
        
        # Só avaliamos playlists com pelo menos 10 músicas (para poder esconder algumas)
        if len(tracks) < 10:
            continue
            
        # Embaralha e esconde 20% das músicas (Estratégia de Hold-out)
        random.shuffle(tracks)
        ponto_corte = int(len(tracks) * 0.8) # 80% para treino
        
        musicas_treino = tracks[:ponto_corte]
        musicas_teste = tracks[ponto_corte:] # Essas são as "repostas certas" que vamos esconder
        
        teste_set[pid] = set(musicas_teste)
        
        # Constrói o grafo SÓ com as músicas de treino
        G_treino.add_node(pid, type='playlist')
        for musica in musicas_treino:
            G_treino.add_node(musica, type='music')
            G_treino.add_edge(pid, musica)

print(f"Grafo de Treino montado: {G_treino.number_of_nodes()} nós.")
print(f"Número de playlists para testar: {len(teste_set)}")

# --- 3. FUNÇÃO DE RECOMENDAÇÃO (Igual ao script anterior) ---
def gerar_top_recomendacoes(grafo, playlist_alvo, k=10):
    if playlist_alvo not in grafo: return []
    
    musicas_conhecidas = set(grafo.neighbors(playlist_alvo))
    candidatos = {} # Dicionário {musica: score}
    
    # Algoritmo Baseado em Caminhos (Path Number) [cite: 161-163]
    for musica in musicas_conhecidas:
        vizinhos = grafo.neighbors(musica) # Outras playlists
        for vizinha in vizinhos:
            if vizinha == playlist_alvo: continue
            
            musicas_da_vizinha = grafo.neighbors(vizinha)
            for nova_musica in musicas_da_vizinha:
                if nova_musica not in musicas_conhecidas:
                    # Conta +1 caminho encontrado
                    candidatos[nova_musica] = candidatos.get(nova_musica, 0) + 1
    
    # Ordena pelo número de caminhos e pega o Top K
    recomendacoes_ordenadas = sorted(candidatos.items(), key=lambda x: x[1], reverse=True)
    return [musica for musica, score in recomendacoes_ordenadas[:k]]

# --- 4. AVALIAÇÃO (Cálculo de Precision e Recall) ---
print("\nRodando previsões... (Isso pode levar um minuto)")

resultados = []

for pid, musicas_escondidas in teste_set.items():
    # O sistema tenta adivinhar 10 músicas
    top_10_recomendado = gerar_top_recomendacoes(G_treino, pid, k=10)
    
    # Verifica quantos acertos (Interseção entre recomendado e escondido)
    acertos = 0
    for musica in top_10_recomendado:
        if musica in musicas_escondidas:
            acertos += 1
            
    # Cálculo das métricas para ESSA playlist
    if len(top_10_recomendado) > 0:
        precision = acertos / len(top_10_recomendado) # De tudo que recomendei, quanto era útil?
    else:
        precision = 0
        
    if len(musicas_escondidas) > 0:
        recall = acertos / len(musicas_escondidas) # De tudo que estava escondido, quanto eu achei?
    else:
        recall = 0
        
    resultados.append({'PID': pid, 'Precision': precision, 'Recall': recall})

# --- 5. RESULTADO FINAL (Média Geral) ---
df_res = pd.DataFrame(resultados)
media_precision = df_res['Precision'].mean()
media_recall = df_res['Recall'].mean()
f1_score = 2 * (media_precision * media_recall) / (media_precision + media_recall)

print("-" * 40)
print("RESULTADOS FINAIS DA REPLICAÇÃO ")
print("-" * 40)
print(f"Precision Média: {media_precision:.4f} (O artigo obteve ~0.2188)")
print(f"Recall Médio:    {media_recall:.4f} (O artigo obteve ~0.7875)")
print(f"F1 Score:        {f1_score:.4f}     (O artigo obteve ~0.3423)")
print("-" * 40)

if media_precision > 0.05:
    print("Conclusão: Seu modelo está aprendendo padrões reais!")
else:
    print("Conclusão: O modelo está com dificuldade (pode precisar de mais dados).")