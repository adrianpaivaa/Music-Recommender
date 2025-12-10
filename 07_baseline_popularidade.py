import json
import os
import random
import pandas as pd
from collections import Counter
import gc

# --- CONFIGURAÇÃO ---
# Usamos a mesma configuração do seu melhor modelo para ser justo
MIN_MUSICAS_NA_PLAYLIST = 30  
MAX_ARQUIVOS = 100 # Não precisa ler tudo para saber o que é popular, 100 já dá a média global

pasta_do_script = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(caminho_dados) if f.endswith('.json')])[:MAX_ARQUIVOS]

print(f"--- INICIANDO BASELINE (TOP POPULAR) ---")
print("Passo 1: Descobrindo quais são as Top 10 músicas do mundo...")

contador_global = Counter()

# 1. CONTAGEM GLOBAL
for nome_arq in arquivos:
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) >= MIN_MUSICAS_NA_PLAYLIST:
                tracks = [t['track_name'] for t in pl['tracks']]
                contador_global.update(tracks)
    gc.collect()

# As 10 mais populares (O "Chute Genérico")
top_10_global = [m for m, qtd in contador_global.most_common(10)]
print("\nAS 10 MÚSICAS MAIS POPULARES (BASELINE):")
for i, m in enumerate(top_10_global):
    print(f"{i+1}. {m}")

print(f"\nPasso 2: Testando se recomendar isso para todo mundo funciona...")

resultados = []
# Vamos testar nas mesmas condições do modelo de grafo
for nome_arq in arquivos[:20]: # Teste rápido em 20 arquivos
    with open(os.path.join(caminho_dados, nome_arq), 'r') as f:
        data = json.load(f)
        for pl in data['playlists']:
            if len(pl['tracks']) < MIN_MUSICAS_NA_PLAYLIST: continue
            
            tracks = [t['track_name'] for t in pl['tracks']]
            
            # Divisão Treino/Teste (igual ao grafo)
            random.shuffle(tracks)
            ponto_corte = int(len(tracks) * 0.8)
            musicas_teste = set(tracks[ponto_corte:])
            
            if len(musicas_teste) == 0: continue

            # A RECOMENDAÇÃO É SEMPRE A MESMA: O TOP 10 GLOBAL
            rec = top_10_global
            
            acertos = len(set(rec) & musicas_teste)
            precision = acertos / len(rec)
            recall = acertos / len(musicas_teste)
            
            resultados.append({'Precision': precision, 'Recall': recall})

df = pd.DataFrame(resultados)
print("="*40)
print("RESULTADO DO BASELINE (MODELO BOBO)")
print(f"Precision: {df['Precision'].mean():.4f}")
print(f"Recall:    {df['Recall'].mean():.4f}")
print("="*40)