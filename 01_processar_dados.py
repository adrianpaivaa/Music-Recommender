import json
import pandas as pd
import os

# --- CONFIGURAÇÃO AUTOMÁTICA DE CAMINHO ---
# 1. Pega a pasta onde este script está salvo (pasta 'src')
pasta_do_script = os.path.dirname(os.path.abspath(__file__))

# 2. Volta um nível (..) para a pasta 'MUSICRECOMMENDER' e entra em 'spotify-million/data'
# A correção principal está aqui: 'spotify-million' (com i) e voltando uma pasta
caminho_dados = os.path.join(pasta_do_script, '..', 'spotify-million', 'data')

print(f"Procurando dados na pasta: {caminho_dados}")

# Verifica se a pasta existe antes de continuar
if not os.path.exists(caminho_dados):
    print("\nERRO: A pasta não foi encontrada!")
    print("Verifique se o nome da pasta 'spotify-million' está escrito corretamente.")
    exit()

# Pega o primeiro arquivo .json que encontrar na pasta
arquivos = [f for f in os.listdir(caminho_dados) if f.endswith('.json')]

if len(arquivos) == 0:
    print("ERRO: Nenhum arquivo .json encontrado dentro da pasta 'data'.")
    exit()

arquivo_para_ler = os.path.join(caminho_dados, arquivos[0])
print(f"Lendo o arquivo: {arquivos[0]} ...")

# --- PROCESSAMENTO (Igual ao Artigo: User -> Song -> Artist) ---
data = []

try:
    with open(arquivo_para_ler, 'r') as f:
        conteudo = json.load(f)
        
        # Vamos processar as playlists
        for playlist in conteudo['playlists']:
            pid = playlist['pid']
            
            for track in playlist['tracks']:
                data.append({
                    'playlist_id': pid,      # No artigo seria o User ID
                    'track_uri': track['track_uri'], # No artigo seria o Song ID
                    'artist_name': track['artist_name'], # No artigo seria o Artist ID
                    'track_name': track['track_name']
                })

    # Cria a tabela
    df = pd.DataFrame(data)

    print("-" * 30)
    print(f"SUCESSO! Processamos {len(df)} linhas.")
    print("Amostra dos dados:")
    print(df.head())
    print("-" * 30)

except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo: {e}")