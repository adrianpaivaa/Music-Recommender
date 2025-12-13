# Music Recommender

Um sistema de recomendação de músicas baseado em análise de grafos bipartidos, detecção de comunidades e uso de Ponderação IIF.

## 📋 Descrição

Este projeto analisa dados do **Spotify Million Playlist Dataset** para descobrir comunidades de músicas e playlists, aplicando técnicas avançadas de processamento de grafos. O sistema oferece duas abordagens principais:

1. **Console Interativo** (`console.py`): busca e recomendação em tempo real baseada em similaridade de playlists.
2. **Análise Exploratória** (`visualizar_cluster.py`): processamento em lote com LSH para detecção e visualização de comunidades musicais.

## 🚀 Funcionalidades

- ✅ Carregamento e processamento de 250 arquivos JSON do Spotify
- ✅ **Smart Pruning** para remoção de músicas raras e playlists pouco informativas
- ✅ **Grafo Bipartido** música–playlist
- ✅ **LSH (Locality Sensitive Hashing)** para redução de complexidade
- ✅ **Louvain** para detecção automática de comunidades
- ✅ **Sistema de Recomendação** com heurística IIF (Inverse Item Frequency)
- ✅ **Exportação GEXF** para visualização dos grafos no Gephi

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior  
- Git  
- pip  

### Clonando o repositório

```bash
git clone https://github.com/adrianpaivaa/Music-Recommender.git
cd Music-Recommender
```

### Instalando dependências

```bash
pip install networkx python-louvain datasketch
```

## 📂 Estrutura de Arquivos

```text
MusicRecommender/
├── spotify-million/
│   ├── data/                    # 250 arquivos JSON do Spotify
│   │   ├── mpd.slice.0-999.json
│   │   ├── mpd.slice.1000-1999.json
│   │   ├── mpd.slice.2000-2999.json
│   │   └── ... (até 250 arquivos)
│   └── README.md
├── src/
│   ├── console.py               # Recomendação interativa
│   ├── visualizar_cluster.py    # Geração de grafos e comunidades
│   ├── analise_dados.py
├── .gitignore
├── LICENSE
└── README.md
```

## 📄 Formato dos Arquivos JSON

Cada arquivo JSON segue o padrão oficial do Spotify Million Playlist Dataset:

```json
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

**Importante:**  
O projeto utiliza apenas **250 arquivos JSON** para otimizar o uso de memória e tempo de execução.  
Caso seja necessário utilizar mais dados, basta adicioná-los em `spotify-million/data/`, mantendo o padrão de nomenclatura `mpd.slice.XXXXX-XXXXX.json`.

## 🔧 Como Executar o Projeto

### 1️⃣ Console Interativo (Recomendação em Tempo Real)

Acesse a pasta `src`:

```bash
cd src
```

Execute o console interativo:

```bash
python console.py
```

**O que esperar:**
1. Leitura e processamento dos arquivos JSON
2. Construção do grafo bipartido
3. Loop interativo de busca por músicas

**Exemplo de uso:**

```text
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
```

### 2️⃣ Análise com LSH e Comunidades

Execute o script de análise estrutural:

```bash
python visualizar_cluster.py
```

**Saída:**
- Arquivo `clusters_otimizado.gexf`

Esse arquivo pode ser aberto no **Gephi** para visualização dos grafos e comunidades detectadas pelo algoritmo Louvain.

## ⚙️ Configurações

### Console (`console.py`)

```python
ARQUIVOS_PARA_LER = 250        # Quantidade de arquivos JSON
MIN_MUSICAS_PLAYLIST = 20     # Mínimo de músicas por playlist
LIMIAR_MUSICAS = 5            # Mínimo de playlists por música
```

### Análise de Comunidades (`visualizar_cluster.py`)

```python
ARQUIVOS = 20
MIN_MUSICAS_PL = 50
LIMIAR_PLAYLISTS = 20
TOP_CLUSTERS = 6
```

## 🏗️ Arquitetura do Sistema

### Console Interativo

1. Leitura dos dados  
2. Construção do grafo bipartido  
3. Smart Pruning  
4. Busca interativa  
5. Cálculo do score IIF  
6. Retorno das Top-15 recomendações  

### Análise com LSH

1. Filtragem inicial dos dados  
2. Construção do grafo bipartido reduzido  
3. Geração de assinaturas MinHash  
4. LSH para detecção de similaridade  
5. Louvain para identificação de comunidades  
6. Exportação para Gephi  

## 🔍 O que é LSH (Locality Sensitive Hashing)?

LSH é uma técnica para encontrar itens similares de forma eficiente, reduzindo a complexidade computacional.

- Evita comparações exaustivas de complexidade \(O(n^2)\)
- Reduz o custo para aproximadamente \(O(n \log n)\)
- Permite gerar grafos visualizáveis mesmo com grandes volumes de dados

No projeto, o LSH é utilizado **exclusivamente para a geração e visualização dos grafos**, não interferindo no sistema de recomendação interativo.

## 📈 Heurística IIF (Inverse Item Frequency)

O sistema de recomendação utiliza a seguinte fórmula:

```math
score(m) = \sum_{pl \in vizinhos(m)} 
\frac{1}{\log(|vizinhos(pl)| + 1) + 0.1}
```

**Intuição:**
- Playlists pequenas e específicas recebem maior peso
- Playlists grandes e genéricas recebem menor peso

## 🎯 Algoritmo Louvain

O algoritmo Louvain detecta comunidades maximizando a modularidade do grafo.

- Identifica clusters temáticos de músicas e playlists
- Não requer número pré-definido de comunidades
- Escalável e eficiente para grafos grandes

## 📄 Artigo Científico

Este repositório acompanha o artigo científico desenvolvido como parte do trabalho acadêmico da disciplina.

- 📘 **Título**: *Sistema de Recomendação Musical Baseado em Grafos Bipartidos e Detecção de Comunidades*
- 👨‍🎓 **Autores**: Adrian Paiva, Heitor Xavier
- 🏫 **Instituição**: CEFET-MG
- 📅 **Ano**: 2025

📎 **Acesso ao PDF**:  
➡️ [Clique aqui para acessar o artigo em PDF](artigo.pdf)

> O artigo descreve detalhadamente a metodologia, a modelagem em grafos, a estratégia de Smart Pruning, o uso de LSH, o algoritmo de Louvain e os resultados qualitativos obtidos com o Spotify Million Playlist Dataset.


## 📝 Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autores

- **Adrian Paiva** — https://github.com/adrianpaivaa  
- **Heitor Xavier** — https://github.com/heitorcostax  

## 🙏 Referências

- Spotify Million Playlist Dataset  
- NetworkX  
- python-louvain  
- Datasketch  
- Gephi  
