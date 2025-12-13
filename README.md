# Music Recommender

Um sistema de recomendação de músicas baseado em análise de grafos bipartidos, detecção de comunidades e uso de Ponderação IIF.

## 📋 Descrição

Este projeto analisa dados do Spotify Million Playlist Dataset para descobrir comunidades de músicas e playlists, aplicando técnicas avançadas de processamento de grafos. O sistema oferece duas abordagens:

1. **Console Interativo** (console.py): Busca e recomendação em tempo real baseada em similaridade de playlists
2. **Análise Exploratória** (visualizar_cluster.py): Processamento em lote com LSH para detecção e visualização de comunidades

## 🚀 Funcionalidades

- ✅ Carregamento e processamento de 250 arquivos JSON (Spotify Million Playlist)
- ✅ *Smart Pruning*: Remove músicas raras e playlists vazias automaticamente
- ✅ *Grafo Bipartido*: Representação música-playlist
- ✅ *LSH (Locality Sensitive Hashing)*: Identificação eficiente de músicas similares
- ✅ *Louvain*: Detecção automática de comunidades
- ✅ *Sistema de Recomendação*: Busca interativa com heurística IIF (Inverse Item Frequency)
- ✅ *Exportação GEXF*: Para visualização dos grafos no Gephi

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Dependências

bash
pip install networkx python-louvain datasketch


## 📂 Estrutura de Arquivos 

O projeto contém a seguinte disposição de arquivos:

```
MusicRecommender/
├── spotify-million/
│   ├── data/                    # 250 arquivos JSON do Spotify
│   │   ├── mpd.slice.0-999.json
│   │   ├── mpd.slice.1000-1999.json
│   │   ├── mpd.slice.2000-2999.json
│   │   └── ... (até 250 arquivos)
│   └── README.md
├── src/
│   ├── console.py               
│   ├── visualizar_cluster.py    
│   ├── analise_dados.py
├── .gitignore
├── LICENSE
└── README.md
```

### Formato dos Arquivos JSON

Cada arquivo JSON segue a seguinte estrutura:
```
json
{
  "playlists": [
    {
      "pid": 1,
      "tracks": [
        {
          "track_uri": "spotify:track:...",
          "track_name": "Song Name",
          "artist_name": "Artist Name"
        }
      ]
    }
  ]
}
```

**Importante**: O projeto mantém apenas 250 arquivos para otimizar performance. Se você precisar adicionar mais dados, coloque-os em spotify-million/data/ com o padrão de nomenclatura mpd.slice.XXXXX-XXXXX.json.

## 🔧 Como Usar

### 1. Console Interativo (Recomendação em Tempo Real)

Execute o programa principal:
```
bash
cd src
python console.py
```

*O que esperar:*
1. Carregamento dos 250 arquivos JSON
2. Loop interativo de busca

**Fluxo de Uso:**


Digite o nome de uma música (ou 'sair'): imagine

Encontrei estas músicas:
[1] Imagine - John Lennon
[2] Imagine - Imagine Dragons
[3] Imagine That - First Aid Kit

Qual delas é a correta? (Digite o número, ou 0 para cancelar): 1

Gerando recomendações baseadas em: 'Imagine - John Lennon'...

QUEM OUVE ISSO TAMBÉM OUVE:
   1. Let It Be - The Beatles (Score: 45.23)
   2. All You Need Is Love - The Beatles (Score: 32.15)
   3. The Long and Winding Road - The Beatles (Score: 28.67)
   ...


### 2. Análise com LSH e Comunidades

Execute o script de análise:
```
bash
cd src
python visualizar_cluster.py
```

**Saída**: clusters_otimizado.gexf (abrir no Gephi)

**Resultado**: Grafo bipartido com comunidades detectadas via Louvain

## ⚙️ Configurações

### Console.py
```
python
ARQUIVOS_PARA_LER = 250         # Número de arquivos JSON a processar
MIN_MUSICAS_PLAYLIST = 20       # Mínimo de músicas por playlist
LIMIAR_MUSICAS = 5              # Mínimo de playlists por música (smart pruning)
```

### Visualizar_cluster.py
```
python
ARQUIVOS = 20                   # Arquivos para análise de comunidades
MIN_MUSICAS_PL = 50             # Mínimo de músicas por playlist (forte)
LIMIAR_PLAYLISTS = 20           # Mínimo de playlists por música
TOP_CLUSTERS = 6                # Número de comunidades a manter
```

## 🏗️ Arquitetura

### Console.py (Recomendação em Tempo Real)


1. Carregamento de dados
   ↓
2. Construção do grafo bipartido
   ↓
3. Smart Pruning (remove outliers)
   ↓
4. Loop interativo:
   - Busca (substring matching)
   - IIF Score (Inverse Item Frequency)
   - Top 15 recomendações


### Visualizar_cluster.py (Análise de Comunidades)


1. Leitura e filtragem de dados
   ↓
2. Grafo bipartido reduzido
   ↓
3. LSH (Locality Sensitive Hashing)
   - MinHash para cada música
   - Detecção de similaridade
   ↓
4. Filtragem por similaridade
   ↓
5. Louvain (detecção de comunidades)
   ↓
6. Top 6 maiores comunidades
   ↓
7. Exportação GEXF (Gephi)


## 📊 Métricas e Smart Pruning

O *Smart Pruning* otimiza a consistência do grafo através de um pipeline automatizado:

1. **Remove músicas raras**: Remoção de faixas com baixa relevância (presentes em < 5 playlists).
2. **Limpeza de playlists vazias**: Exclusão automática de playlists que se tornaram vazias após a filtragem.

Isso torna o grafo mais denso e relevante para recomendações.

## 🔍 O que é LSH (Locality Sensitive Hashing)?

LSH é uma técnica para encontrar itens similares rapidamente:

1. Cada música é representada como um *MinHash* (assinatura) baseado nas playlists que contém
2. Músicas com assinaturas similares são identificadas em $\mathcal{O}(\log n)$ tempo
3. Apenas pares similares (threshold ≥ 0.5) são conectados

No projeto, o LSH é aplicado especificamente para gerar grafos de similaridades de forma mais rápida e otimizada. Como o Spotify Million Playlist Dataset é massivo (milhões de itens), processar o grafo inteiro com comparações exaustivas complexidade $\mathcal{O}(n^2)$ seria inviável; o LSH reduz isso para $\mathcal{O}(n \log n)$, permitindo filtrar conexões relevantes e exibir resultados visuais (como comunidades no Gephi) sem sobrecarregar recursos computacionais. Ele não afeta o sistema de recomendações interativo, que usa heurísticas mais leves.
 

## 📈 Heurística IIF (Inverse Item Frequency)

O sistema de recomendação usa a fórmula:

$$\text{score}(m) = \sum_{\text{pl} \in \text{vizinhos}(m)} \frac{1}{\log(|\text{vizinhos}(pl)| + 1) + 0.1}$$

**Intuição**:
- Playlists *pequenas e específicas* pesam MAIS (mais informativas)
- Playlists *gigantes e genéricas* pesam MENOS (menos informativos)

Exemplo:
- Playlist com 20 músicas: peso ≈ 0.32 (específica)
- Playlist com 100 músicas: peso ≈ 0.21 (genérica)

## 🎯 Algoritmo Louvain

O algoritmo Louvain é um método hierárquico que detecta comunidades maximizando a modularidade – uma métrica que avalia a densidade interna de grupos versus conexões externas no grafo.

- No contexto do projeto, identifica clusters temáticos de músicas e playlists baseados em co-ocorrências frequentes, revelando padrões como "rock clássico" ou "pop".
- Não requer um número pré-definido de clusters, adaptando-se automaticamente à estrutura do grafo bipartido.
- Rápido e escalável, processa eficientemente redes com milhares de nós, como o dataset Spotify.

## 📝 Licença

Este projeto está devidamente licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👤 Autores

- **Adrian Paiva** — [GitHub](https://github.com/adrianpaivaa)
- **Heitor Xavier** — [GitHub](https://github.com/heitorcostax)

## 🙏 Referências

- [Spotify Million Playlist Dataset](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge)
- [NetworkX](https://networkx.org/)
- [python-louvain](https://github.com/taynaud/python-louvain)
- [Datasketch](https://github.com/ekzhu/datasketch)
- [Gephi](https://gephi.org/)
