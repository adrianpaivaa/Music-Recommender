# Music Recommender

Um sistema de recomendação de músicas baseado em análise de grafos bipartidos, detecção de comunidades e Locality Sensitive Hashing (LSH).

## 📋 Descrição

Este projeto analisa dados do Spotify Million Playlist Dataset para descobrir comunidades de músicas e playlists, utilizando:

- **Grafo Bipartido**: Representação música-playlist
- **LSH (Locality Sensitive Hashing)**: Identificação eficiente de músicas similares
- **Louvain**: Detecção de comunidades em grafos
- **NetworkX**: Análise e manipulação de grafos
- **Gephi**: Visualização e análise exploratória

## 🚀 Funcionalidades

- ✅ Processamento de grandes volumes de dados (Spotify Million Playlist)
- ✅ Filtragem inteligente de playlists e músicas (força mínima)
- ✅ Aplicação de LSH para encontrar similaridades eficientemente
- ✅ Detecção automática de comunidades
- ✅ Exportação em formato GEXF para visualização no Gephi

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Dependências

```bash
pip install networkx python-louvain datasketch
```

## 🔧 Uso

### Executar análise completa

```bash
python src/visualizar_cluster.py
```

**Saída**: `comunidades_globais_otimizado.gexf`

### Visualizar no Gephi

1. Abra o Gephi
2. Importe `comunidades_globais_otimizado.gexf`
3. Colore os nós por `modularity_class` para ver as comunidades

## ⚙️ Configuração

Edite as variáveis de configuração em `src/visualizar_cluster.py`:

```python
ARQUIVOS = 20              # Número de arquivos a processar
MIN_MUSICAS_PL = 50        # Mínimo de músicas por playlist
LIMIAR_PLAYLISTS = 20      # Mínimo de playlists por música
TOP_CLUSTERS = 6           # Número de comunidades a manter
```

## 🏗️ Arquitetura

```
Dados Spotify Million
        ↓
    Filtros
        ↓
Grafo Bipartido (música-playlist)
        ↓
  LSH (similaridade)
        ↓
Grafo Filtrado
        ↓
  Louvain (comunidades)
        ↓
   Grafo Final
        ↓
GEXF (Gephi)
```

## 📊 Estrutura do Projeto

```
├── src/
│   ├── visualizar_cluster.py     # Script principal
│   ├── analise_dados.py          # Análise de dados
│   ├── console.py                # Interface console
│   ├── validacao_modelo.py       # Validação
│   └── visualizar_cluster.py     # Visualização
├── spotify-million/
│   ├── data/                     # Dados do Spotify (não versionado)
│   └── README.md
├── .gitignore
├── LICENSE
└── README.md
```

## 🔍 O que é LSH?

Locality Sensitive Hashing é uma técnica para encontrar itens similares rapidamente em grandes conjuntos de dados. No contexto deste projeto:

1. Cada música é representada como um MinHash baseado nas playlists que contém
2. Músicas com assinaturas similares são identificadas eficientemente
3. Apenas pares similares são conectados no grafo

Isso reduz drasticamente a complexidade computacional comparado a comparações diretas.

## 📈 Louvain

O algoritmo de Louvain detecta comunidades maximizando a modularidade do grafo. Comunidades representam grupos de músicas frequentemente encontradas juntas em playlists.

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👤 Autor

Adrian Paiva - [GitHub](https://github.com/adrianpaivaa)

## 🙏 Agradecimentos

- [Spotify Million Playlist Dataset](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge)
- [NetworkX](https://networkx.org/)
- [python-louvain](https://github.com/taynaud/python-louvain)
- [Datasketch](https://github.com/ekzhu/datasketch)
- [Gephi](https://gephi.org/)

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
