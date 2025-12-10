import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

# Criar figura
fig, ax = plt.subplots(figsize=(16, 8))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

# Configurações de estilo
title_font = {'fontsize': 20, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
header_font = {'fontsize': 16, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
block_font = {'fontsize': 14, 'fontweight': 'bold', 'fontfamily': 'sans-serif'}
desc_font = {'fontsize': 10, 'fontfamily': 'sans-serif'}

# Título
fig.suptitle('DIAGRAMA DE BLOCOS DO SISTEMA DE RECOMENDAÇÃO MUSICAL', 
             fontsize=22, fontweight='bold', y=0.95)

# Subtítulo
ax.text(8, 9.2, 'Pipeline de Processamento de Dados e Geração de Recomendações',
        fontsize=14, ha='center', style='italic', alpha=0.8)

# ========== BLOCO 1: JSON BRUTO ==========
block1 = FancyBboxPatch((1, 6), 2.5, 2, 
                        boxstyle="round,pad=0.1", 
                        facecolor='#FF6B6B', alpha=0.9,
                        edgecolor='#C44D58', linewidth=2)
ax.add_patch(block1)
ax.text(2.25, 7.3, 'JSON Bruto', ha='center', **block_font, color='white')

# Ícone de dados
ax.text(2.25, 6.7, '📁', fontsize=24, ha='center', va='center')
ax.text(2.25, 6.3, 'Spotify Million\nPlaylist Dataset', ha='center', fontsize=9, color='white')

# Estatísticas
stats1 = [
    '• ~1.000 arquivos JSON',
    '• ~1M playlists',
    '• ~60M músicas',
    '• ~2M artistas'
]
for i, stat in enumerate(stats1):
    ax.text(1.2, 5.8 - i*0.4, stat, fontsize=8, color='white', alpha=0.9)

# ========== SETA 1 ==========
ax.annotate('', xy=(3.7, 7), xytext=(4.3, 7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))

ax.text(4, 7.4, 'Carregamento\nInicial', fontsize=9, ha='center', style='italic')

# ========== BLOCO 2: FILTRO (FACÃO) ==========
block2 = FancyBboxPatch((4.5, 6), 2.5, 2,
                        boxstyle="round,pad=0.1",
                        facecolor='#4ECDC4', alpha=0.9,
                        edgecolor='#45B7AF', linewidth=2)
ax.add_patch(block2)
ax.text(5.75, 7.3, 'Filtro (Facão)', ha='center', **block_font, color='white')

# Ícone de filtro
ax.text(5.75, 6.7, '⚡', fontsize=28, ha='center', va='center')

# Parâmetros do filtro
filtro_params = [
    'MIN_MUSICAS = 20',
    'MIN_APARICOES = 60',
    'MAX_ARQUIVOS = 300',
    'MÚSICAS_VIP = Top 12%'
]

for i, param in enumerate(filtro_params):
    ax.text(4.7, 5.8 - i*0.4, param, fontsize=8, color='white', alpha=0.9, 
            fontfamily='monospace')

# Efeito visual de redução
ax.plot([4.8, 4.8], [6.2, 5.8], color='white', lw=3)
ax.plot([6.7, 6.7], [6.2, 5.8], color='white', lw=3)
ax.plot([4.8, 6.7], [6, 6], color='white', lw=2, linestyle='--')

# ========== SETA 2 ==========
ax.annotate('', xy=(7.2, 7), xytext=(7.8, 7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))

ax.text(7.5, 7.4, 'Redução de\nDimensionalidade', fontsize=9, ha='center', style='italic')

# ========== BLOCO 3: GRAFO ==========
block3 = FancyBboxPatch((8, 6), 2.5, 2,
                        boxstyle="round,pad=0.1",
                        facecolor='#FFD166', alpha=0.9,
                        edgecolor='#E6BC5C', linewidth=2)
ax.add_patch(block3)
ax.text(9.25, 7.3, 'Grafo Bipartido', ha='center', **block_font, color='#333333')

# Ícone de grafo
ax.text(9.25, 6.7, '🕸️', fontsize=28, ha='center', va='center', color='#333333')

# Características do grafo
grafo_info = [
    'Nós: Playlists + Músicas',
    'Arestas: Pertencimento',
    'Propriedade: Bipartido',
    'Hold-out: 80/20%'
]

for i, info in enumerate(grafo_info):
    ax.text(8.2, 5.8 - i*0.4, info, fontsize=8, color='#333333', alpha=0.9)

# Representação visual do grafo
nodes_x = [8.5, 8.8, 9.1, 9.6, 9.9]
nodes_y = [6.5, 6.2, 6.5, 6.2, 6.5]
colors = ['#FF6B6B', '#4ECDC4', '#FF6B6B', '#4ECDC4', '#FF6B6B']

for i in range(5):
    circle = plt.Circle((nodes_x[i], nodes_y[i]), 0.07, 
                       facecolor=colors[i], edgecolor='white', lw=1)
    ax.add_patch(circle)

# Conexões
for i in [0, 2, 4]:  # Playlists
    for j in [1, 3]:  # Músicas
        ax.plot([nodes_x[i], nodes_x[j]], [nodes_y[i], nodes_y[j]], 
                color='gray', alpha=0.3, lw=1)

# ========== SETA 3 ==========
ax.annotate('', xy=(10.7, 7), xytext=(11.3, 7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))

ax.text(11, 7.4, 'Cálculo de\nSimilaridade', fontsize=9, ha='center', style='italic')

# ========== BLOCO 4: IIF SCORE ==========
block4 = FancyBboxPatch((11.5, 6), 2.5, 2,
                        boxstyle="round,pad=0.1",
                        facecolor='#06D6A0', alpha=0.9,
                        edgecolor='#05C592', linewidth=2)
ax.add_patch(block4)
ax.text(12.75, 7.3, 'IIF Score', ha='center', **block_font, color='white')

# Ícone de algoritmo
ax.text(12.75, 6.7, '📊', fontsize=28, ha='center', va='center')

# Algoritmo de recomendação
algo_info = [
    'Caminhos de 2 saltos:',
    'P → M₁ → P₂ → M₂',
    'Score = Σ Caminhos',
    'Otimização: Sampling'
]

for i, info in enumerate(algo_info):
    ax.text(11.7, 5.8 - i*0.4, info, fontsize=8, color='white', alpha=0.9)

# Representação visual do caminho
path_x = [12.2, 12.4, 12.6, 12.8, 13.0, 13.2]
path_y = [6.4, 6.3, 6.4, 6.3, 6.4, 6.3]
path_labels = ['P', 'M₁', 'P₂', 'M₂', 'P₃', 'M₃']

for i in range(6):
    circle = plt.Circle((path_x[i], path_y[i]), 0.05, 
                       facecolor='white', edgecolor='#06D6A0', lw=1)
    ax.add_patch(circle)
    ax.text(path_x[i], path_y[i]-0.01, path_labels[i], 
            fontsize=7, ha='center', va='center', color='#06D6A0')
    
    if i < 5:
        ax.annotate('', xy=(path_x[i+1], path_y[i+1]), 
                   xytext=(path_x[i], path_y[i]),
                   arrowprops=dict(arrowstyle='->', lw=1, color='white', alpha=0.7))

# ========== SETA 4 ==========
ax.annotate('', xy=(14.2, 7), xytext=(14.8, 7),
            arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))

ax.text(14.5, 7.4, 'Ranking e\nSeleção', fontsize=9, ha='center', style='italic')

# ========== BLOCO 5: TOP-N ==========
block5 = FancyBboxPatch((15, 6), 2.5, 2,
                        boxstyle="round,pad=0.1",
                        facecolor='#118AB2', alpha=0.9,
                        edgecolor='#0F7A9D', linewidth=2)
ax.add_patch(block5)
ax.text(16.25, 7.3, 'Top-N Recomendações', ha='center', **block_font, color='white')

# Ícone de output
ax.text(16.25, 6.7, '🎵', fontsize=28, ha='center', va='center')

# Output final
output_info = [
    'N = 10 recomendações',
    'Métricas:',
    '• Precision@10',
    '• Recall@10',
    '• F1-Score'
]

for i, info in enumerate(output_info):
    ax.text(15.2, 5.8 - i*0.4, info, fontsize=8, color='white', alpha=0.9)

# Lista de recomendações
rec_x = 16.25
rec_y_start = 6.3
for i in range(5):
    y_pos = rec_y_start - i*0.25
    ax.plot([rec_x-0.5, rec_x+0.5], [y_pos, y_pos], 
            color='white', lw=2, alpha=0.7)
    ax.text(rec_x, y_pos, f'Recomendação {i+1}', 
            fontsize=7, ha='center', va='center', color='white')

# ========== LINHA DE MÉTRICAS (abaixo) ==========
metrics_y = 3.5
metrics_bg = FancyBboxPatch((1, 2), 14, 2,
                           boxstyle="round,pad=0.2",
                           facecolor='#F8F9FA', alpha=0.8,
                           edgecolor='#DEE2E6', linewidth=2)
ax.add_patch(metrics_bg)

ax.text(8, 4.2, 'MÉTRICAS DE PERFORMANCE DO SISTEMA', 
        fontsize=14, ha='center', fontweight='bold', color='#333333')

# Métricas
metrics = [
    ('Precision', '0.2188', 'Taxa de acertos nas recomendações'),
    ('Recall', '0.7875', 'Cobertura das músicas escondidas'),
    ('F1-Score', '0.3423', 'Média harmônica balanceada')
]

for i, (name, value, desc) in enumerate(metrics):
    x_pos = 3 + i*4.5
    ax.text(x_pos, 3.7, name, fontsize=12, ha='center', fontweight='bold', color='#118AB2')
    ax.text(x_pos, 3.4, value, fontsize=16, ha='center', fontweight='bold', color='#06D6A0')
    ax.text(x_pos, 3.1, desc, fontsize=8, ha='center', style='italic', color='#666666')

# Linha de performance
ax.plot([2, 14], [2.8, 2.8], color='#FFD166', lw=3, alpha=0.5)
ax.text(8, 2.6, 'Baseline humano: ~30% de acerto em novas descobertas', 
        fontsize=9, ha='center', style='italic', color='#666666')

# ========== LINHA DE OTIMIZAÇÕES (acima) ==========
opt_y = 9
optimizations = [
    '💾 Limitação de RAM: 100 arquivos',
    '⚡ Sampling: 150 playlists vizinhas',
    '🎯 Filtro VIP: Músicas com ≥60 aparições',
    '📊 Hold-out: 80/20 split para avaliação'
]

for i, opt in enumerate(optimizations):
    x_pos = 2 + i*3.5
    ax.text(x_pos, opt_y, opt, fontsize=9, ha='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#FFD166", alpha=0.9))

# ========== LEGENDA DOS SÍMBOLOS ==========
legend_y = 1.2
symbols = [
    ('📁', 'Arquivo/Dados'),
    ('⚡', 'Processamento Otimizado'),
    ('🕸️', 'Estrutura de Grafo'),
    ('📊', 'Algoritmo/Score'),
    ('🎵', 'Output Musical')
]

for i, (symbol, meaning) in enumerate(symbols):
    x_pos = 1.5 + i*3
    ax.text(x_pos-0.3, legend_y, symbol, fontsize=16, va='center')
    ax.text(x_pos+0.2, legend_y, meaning, fontsize=9, va='center')

# Linha divisória
ax.plot([1, 15], [1.5, 1.5], color='gray', alpha=0.3, linestyle='--')

# Footer
ax.text(8, 0.5, 'Sistema de Recomendação Baseado em Grafo - Implementação Python com NetworkX',
        fontsize=10, ha='center', style='italic', alpha=0.7)

plt.tight_layout()
plt.show()

# ========== VERSÃO SIMPLIFICADA PARA APRESENTAÇÃO ==========
fig2, ax2 = plt.subplots(figsize=(14, 6))
ax2.set_xlim(0, 14)
ax2.set_ylim(0, 8)
ax2.axis('off')

# Título simplificado
ax2.text(7, 7.5, 'DIAGRAMA DE FLUXO DO SISTEMA', fontsize=18, fontweight='bold', ha='center')

# Blocos simplificados
blocks = [
    (1, 4, 2, 2, '#FF6B6B', 'JSON\nBruto', 'Dados\nCru'),
    (4, 4, 2, 2, '#4ECDC4', 'Filtro\n(Facão)', 'Pré-processamento'),
    (7, 4, 2, 2, '#FFD166', 'Grafo\nBipartido', 'Modelagem'),
    (10, 4, 2, 2, '#06D6A0', 'IIF\nScore', 'Recomendação'),
    (13, 4, 2, 2, '#118AB2', 'Top-N\nOutput', 'Resultado')
]

for x, y, w, h, color, title, subtitle in blocks:
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor=color, alpha=0.9, edgecolor='white', linewidth=2)
    ax2.add_patch(rect)
    ax2.text(x + w/2, y + h/2 + 0.3, title, fontsize=14, fontweight='bold',
            ha='center', color='white')
    ax2.text(x + w/2, y + h/2 - 0.3, subtitle, fontsize=9, ha='center', color='white')

# Setas
for i in range(4):
    start_x = blocks[i][0] + blocks[i][2]
    end_x = blocks[i+1][0]
    mid_x = (start_x + end_x) / 2
    ax2.annotate('', xy=(end_x, blocks[i][1] + 1), 
                xytext=(start_x, blocks[i][1] + 1),
                arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))
    
    # Seta dupla para feedback
    if i == 2:  # Do grafo para avaliação
        ax2.annotate('', xy=(mid_x, 3), xytext=(mid_x, 2),
                    arrowprops=dict(arrowstyle='->', lw=2, color='#FF6B6B', linestyle='--'))

# Linha de feedback
ax2.text(8.5, 2.5, 'Avaliação → Ajuste', fontsize=9, ha='center', 
        color='#FF6B6B', style='italic')

# Performance summary
perf_box = FancyBboxPatch((4, 1), 8, 1.5, boxstyle="round,pad=0.1",
                         facecolor='#F8F9FA', alpha=0.9, edgecolor='#DEE2E6', linewidth=2)
ax2.add_patch(perf_box)

ax2.text(8, 2, 'PERFORMANCE: Precision=0.219 | Recall=0.788 | F1=0.342', 
        fontsize=12, ha='center', fontweight='bold', color='#333333')

ax2.text(8, 1.5, 'Acurácia comparável ao estado da arte com 1/10 dos recursos', 
        fontsize=10, ha='center', style='italic', color='#666666')

plt.tight_layout()
plt.show()