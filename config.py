"""
config.py — Constantes compartilhadas por todas as partes do jogo.

Mudar um valor aqui muda o jogo inteiro (tamanho do plano, distâncias mínimas,
dificuldade etc.), sem precisar mexer no código das partes.
"""

# ---------------------------------------------------------------- Janela ----
LARGURA, ALTURA = 1240, 680
FPS = 60
TITULO = "Deslocamento com Obstáculos - GAAL"

# ------------------------------------------------------- Plano cartesiano ----
# Limites do plano em UNIDADES (cada quadradinho da grade = 1 unidade).
PLANO_XMIN, PLANO_XMAX = -12, 12
PLANO_YMIN, PLANO_YMAX = -7, 7
ESCALA = 38  # pixels por unidade

# Retângulos da tela (x, y, largura, altura) em pixels
RECT_PLANO = (16, 64, (PLANO_XMAX - PLANO_XMIN) * ESCALA, (PLANO_YMAX - PLANO_YMIN) * ESCALA)
RECT_LATERAL = (944, 64, 280, 600)
RECT_MENSAGEM = (16, 606, RECT_PLANO[2], 58)

# --------------------------------------------- Pontos de partida e chegada ----
X_PARTIDA = -10.5          # linha de largada (reta vertical x = -10.5)
X_CHEGADA = 10.5           # x do ponto de chegada
FAIXA_Y_CHEGADA = 3.0      # y da chegada é sorteado em [-3, 3]
SEPARACAO_PARTIDAS = 2.5   # cada partida fica 2.5 acima/abaixo da chegada
RAIO_CHEGADA = 0.7         # tocar este círculo = chegou

# ------------------------------------------------------------ Jogadores ----
RAIO_JOGADOR = 0.25        # "tamanho" do marcador usado na colisão

# ----------------------------------------------------------- Obstáculos ----
# Faixa em x onde os obstáculos podem nascer (longe da largada e da chegada)
OBST_XMIN, OBST_XMAX = -8.5, 8.5
MARGEM_BORDA = 0.8                 # distância mínima das bordas de cima/baixo
DIST_MIN_ENTRE_OBSTACULOS = 0.9    # folga mínima entre dois obstáculos (> diâmetro do marcador)
DIST_MIN_DOS_PONTOS = 2.0          # folga mínima até partidas e chegada

# --------------------------------------------------------------- Regras ----
PUNICAO_TURNOS = 1  # quantas vezes o jogador fica sem jogar depois de bater

# ---------------------------------------------------------- Dificuldade ----
# raio e abertura (em graus) do setor circular são sorteados nessas faixas;
# "desvio" é o quanto (em graus) o setor pode se afastar da direção da chegada.
DIFICULDADES = {
    "Fácil":   {"triangulos": 3, "quadrados": 3, "raio": (2.5, 5.0), "abertura": (60, 140), "desvio": 40},
    "Médio":   {"triangulos": 4, "quadrados": 4, "raio": (2.0, 4.5), "abertura": (45, 110), "desvio": 60},
    "Difícil": {"triangulos": 5, "quadrados": 4, "raio": (1.6, 4.0), "abertura": (30, 90),  "desvio": 80},
}
ORDEM_DIFICULDADES = ["Fácil", "Médio", "Difícil"]
DIFICULDADE_PADRAO = "Médio"
