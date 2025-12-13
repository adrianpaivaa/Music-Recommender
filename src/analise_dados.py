import json
import os
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spotify-million', 'data')
arquivos = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.json')])[:100]

print(f"Lendo {len(arquivos)} arquivos...")

todas_musicas = []

# Coleta todas as musicas de todas as playlists disponíveis
for arquivo in arquivos:
    with open(os.path.join(pasta_dados, arquivo), 'r') as f:
        dados = json.load(f)
        for playlist in dados['playlists']:
            musicas = [track['track_uri'] for track in playlist['tracks']]
            todas_musicas.extend(musicas)

# Conta frequencia de cada musica e ordena por popularidade
contagem = Counter(todas_musicas)
df = pd.DataFrame.from_dict(contagem, orient='index', columns=['contagem'])
df = df.sort_values(by='contagem', ascending=False).reset_index(drop=True)

# Calcula e printa os dados
total_musicas_unicas = len(df)
total_plays = df['contagem'].sum()
top_20_porcento = int(total_musicas_unicas * 0.2)
plays_no_top_20 = df.head(top_20_porcento)['contagem'].sum()
porcentagem_plays = (plays_no_top_20 / total_plays) * 100

musicas_1_play = len(df[df['contagem'] == 1])
porcentagem_1_play = (musicas_1_play / total_musicas_unicas) * 100

print(f"Total de musicas unicas: {total_musicas_unicas}")
print(f"Top 20% concentram {porcentagem_plays:.2f}% das reproducoes")
print(f"Musicas com apenas 1 play: {musicas_1_play} ({porcentagem_1_play:.2f}%)")

plt.figure(figsize=(10, 6))
plt.plot(df.index, df['contagem'], color='blue', linewidth=2)
plt.title('Distribuicao de Popularidade das Musicas')
plt.xlabel('Musicas (Rankeadas por Popularidade)')
plt.ylabel('Numero de Aparicoes em Playlists')
plt.grid(True, which="both", ls="-", alpha=0.2)

plt.savefig('grafico_cauda_longa.png')
print("Gráfico gerado.")
plt.show()