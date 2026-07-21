"""
plotagem.py

Gera os graficos finais da barra 1D apos a simulacao no CalculiX:

    1) Geometria DEFORMADA (distorcida): mostra a barra original
       (linha fina/cinza) e a barra deslocada pelos deslocamentos
       calculados (linha grossa/colorida), para visualizar como ela
       se deformou sob o carregamento.

    2) Geometria SEM deformacao, colorida por tensao: a barra mantem
       sua forma original (reta), mas cada ponto e colorido numa
       escala azul (valor baixo) -> vermelho (valor alto) conforme o
       campo escolhido pelo usuario (von Mises, Tresca, sigma axial,
       sigma max, sigma min, epsilon max, epsilon min).

Usa apenas matplotlib (ja disponivel no ambiente de file-creation).
"""

import matplotlib
matplotlib.use("Agg")  # backend sem GUI, compativel com qualquer SO/ambiente
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np


CAMPOS_DISPONIVEIS = {
    "von_mises": "Tensao equivalente de von Mises",
    "tresca": "Tensao equivalente de Tresca",
    "sigma_axial": "Tensao normal axial (sigma_xx)",
    "sigma_max": "Tensao principal maxima",
    "sigma_min": "Tensao principal minima",
    "epsilon_max": "Deformacao principal maxima",
    "epsilon_min": "Deformacao principal minima",
}


def plotar_geometria_deformada(nodes: dict, disp: dict, fator_escala: float,
                                  caminho_saida) -> None:
    """
    Plota a barra original (cinza, fina) e a barra deformada (azul,
    grossa), com os deslocamentos amplificados por fator_escala.

    Escolhe automaticamente qual eixo transversal (Y ou Z) mostrar no
    grafico 2D, usando o que tiver maior deslocamento absoluto -- a
    flexao/torcao de uma barra 1D pode acontecer em qualquer plano
    dependendo de como a carga foi aplicada, e um grafico 2D só pode
    mostrar um plano por vez.
    """
    node_ids_ordenados = sorted(nodes.keys())

    max_disp_y = max((abs(disp.get(n, (0, 0, 0))[1]) for n in node_ids_ordenados), default=0.0)
    max_disp_z = max((abs(disp.get(n, (0, 0, 0))[2]) for n in node_ids_ordenados), default=0.0)
    eixo_transversal = 2 if max_disp_z > max_disp_y else 1
    nome_eixo = "Z" if eixo_transversal == 2 else "Y"

    x_orig = [nodes[n][0] for n in node_ids_ordenados]
    y_orig = [nodes[n][eixo_transversal] for n in node_ids_ordenados]

    x_def = []
    y_def = []
    for n in node_ids_ordenados:
        u = disp.get(n, (0.0, 0.0, 0.0))
        x_def.append(nodes[n][0] + u[0] * fator_escala)
        y_def.append(nodes[n][eixo_transversal] + u[eixo_transversal] * fator_escala)

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(x_orig, y_orig, "o-", color="lightgray", linewidth=1.5,
            markersize=4, label="Original geometry")
    ax.plot(x_def, y_def, "o-", color="#1f5fa8", linewidth=2.5,
            markersize=5, label=f"Deformad geometry (distortion factor > {fator_escala:.1f}x)")

    ax.set_xlabel("X [mm]")
    ax.set_ylabel(f"{nome_eixo} [mm]")
    #ax.set_title(f"Deformacao da barra no plano X-{nome_eixo} (geometria distorcida)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)


def plotar_geometria_colorida_por_campo(nodes: dict, valores_por_no: dict,
                                           nome_campo: str, caminho_saida) -> None:
    """
    Plota a barra na geometria ORIGINAL (sem distorcer), mas colorida
    ao longo do seu comprimento conforme valores_por_no -- escala de
    cores azul (valor minimo) a vermelho (valor maximo).
    """
    node_ids_ordenados = sorted(nodes.keys())

    x = np.array([nodes[n][0] for n in node_ids_ordenados])
    y = np.array([nodes[n][1] for n in node_ids_ordenados])
    valores = np.array([valores_por_no.get(n, 0.0) for n in node_ids_ordenados])
    biggest = max(valores)

    # Monta segmentos de linha entre nos consecutivos, cada um colorido
    # pela media do valor nos dois nos que o formam (LineCollection e a
    # forma padrao do matplotlib de colorir uma linha por segmentos).
    pontos = np.array([x, y]).T.reshape(-1, 1, 2)
    segmentos = np.concatenate([pontos[:-1], pontos[1:]], axis=1)
    valores_segmento = (valores[:-1] + valores[1:]) / 2.0

    fig, ax = plt.subplots(figsize=(10, 4))

    lc = LineCollection(segmentos, cmap="coolwarm", linewidths=7)
    lc.set_array(valores_segmento)
    linha = ax.add_collection(lc)

    ax.scatter(x, y, c=valores, cmap="coolwarm", s=40, zorder=3,
               edgecolors="black", linewidths=0.5)

    ax.set_xlim(x.min() - (x.max() - x.min()) * 0.05, x.max() + (x.max() - x.min()) * 0.05)
    margem_y = max(1.0, (y.max() - y.min()) * 0.5 + 5.0)
    ax.set_ylim(y.min() - margem_y, y.max() + margem_y)

    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    #ax.set_title(f"{CAMPOS_DISPONIVEIS.get(nome_campo, nome_campo)} ao longo da barra \n max = {biggest}")
    ax.set_title(f" max = {biggest}")
    ax.grid(True, alpha=0.3)
    

    cbar = fig.colorbar(linha, ax=ax)
    #cbar.set_label(CAMPOS_DISPONIVEIS.get(nome_campo, nome_campo))

    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)


def escolher_fator_escala_automatico(nodes: dict, disp: dict) -> float:
    """
    Calcula um fator de escala automatico para a plotagem da geometria
    deformada, de forma que o maior deslocamento visualizado corresponda
    a aproximadamente 15% do comprimento total da barra (heuristica
    simples e robusta para deslocamentos pequenos tipicos de FEM linear).
    """
    xs = [coord[0] for coord in nodes.values()]
    comprimento_total = max(xs) - min(xs)
    if comprimento_total <= 0:
        comprimento_total = 1.0

    maior_deslocamento = 0.0
    for (ux, uy, uz) in disp.values():
        maior_deslocamento = max(maior_deslocamento, abs(ux), abs(uy), abs(uz))

    if maior_deslocamento <= 1e-12:
        return 1.0  # sem deslocamento relevante, nao amplifica

    fator = (0.15 * comprimento_total) / maior_deslocamento
    return max(1.0, fator)
