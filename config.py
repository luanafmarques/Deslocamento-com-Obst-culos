"""
config.py — Constantes compartilhadas por todas as partes do jogo.

Mudar um valor aqui muda o jogo inteiro (tamanho do plano, distâncias mínimas,
dificuldade etc.), sem precisar mexer no código das partes.
"""
import sys

# True quando o jogo roda no navegador (versão web gerada pelo pygbag)
NO_NAVEGADOR = sys.platform == "emscripten"

# ---------------------------------------------------------------- Janela ----
# Layout de PC: desenhado em 1240x680. No navegador a área do jogo cresce para
# ter a mesma proporção da janela (sem faixas nos lados) e o conteúdo fica
# centralizado, deslocado por (X0, Y0).
# Layout de CELULAR: área do jogo com só 420 px de altura (tudo aparece maior),
# plano ocupando quase a tela toda e um painel compacto à direita.
BASE_LARGURA, BASE_ALTURA = 1240, 680
ALTURA_CELULAR = 420


def medidas_da_janela():
    """(largura, altura) da janela do navegador em px, ou None fora do navegador."""
    if not NO_NAVEGADOR:
        return None
    try:
        import platform
        return platform.window.innerWidth, platform.window.innerHeight
    except Exception:
        return None


def eh_celular(medidas):
    """Tela pequena (o lado menor tem menos de 600 px) = layout de celular."""
    return medidas is not None and min(medidas) < 600


def tamanho_para(medidas):
    """Tamanho da área do jogo com a mesma proporção da janela."""
    if medidas is None:
        return BASE_LARGURA, BASE_ALTURA
    proporcao = medidas[0] / medidas[1]
    if eh_celular(medidas):
        proporcao = max(1.8, min(3.0, proporcao))
        return round(ALTURA_CELULAR * proporcao), ALTURA_CELULAR
    proporcao = max(1.2, min(3.5, proporcao))
    if proporcao >= BASE_LARGURA / BASE_ALTURA:
        return round(BASE_ALTURA * proporcao), BASE_ALTURA
    return BASE_LARGURA, round(BASE_LARGURA / proporcao)


_medidas = medidas_da_janela()
CELULAR = eh_celular(_medidas)
LARGURA, ALTURA = tamanho_para(_medidas)
X0, Y0 = (LARGURA - BASE_LARGURA) // 2, (ALTURA - BASE_ALTURA) // 2
FPS = 60
TITULO = "Deslocamento com Obstáculos - GAAL"

# ------------------------------------------------------- Plano cartesiano ----
# Limites do plano em UNIDADES (cada quadradinho da grade = 1 unidade).
PLANO_XMIN, PLANO_XMAX = -12, 12
PLANO_YMIN, PLANO_YMAX = -7, 7
ESCALA = 38  # pixels por unidade

# Retângulos da tela (x, y, largura, altura) em pixels
if CELULAR:
    _margem, _painel = 6, 214
    _escala = min((LARGURA - _painel - 3 * _margem) / (PLANO_XMAX - PLANO_XMIN),
                  (ALTURA - 2 * _margem) / (PLANO_YMAX - PLANO_YMIN))
    _pl = round((PLANO_XMAX - PLANO_XMIN) * _escala)
    _pa = round((PLANO_YMAX - PLANO_YMIN) * _escala)
    _painel = min(LARGURA - _pl - 3 * _margem, 280)      # painel não fica largo demais
    _x = (LARGURA - (_pl + _painel + 3 * _margem)) // 2  # centraliza plano + painel
    RECT_PLANO = (_x + _margem, (ALTURA - _pa) // 2, _pl, _pa)
    RECT_LATERAL = (_x + _pl + 2 * _margem, _margem, _painel, ALTURA - 2 * _margem)
    RECT_MENSAGEM = None  # no celular a mensagem aparece flutuando em cima do plano
else:
    RECT_PLANO = (X0 + 16, Y0 + 64, (PLANO_XMAX - PLANO_XMIN) * ESCALA, (PLANO_YMAX - PLANO_YMIN) * ESCALA)
    RECT_LATERAL = (X0 + 944, Y0 + 64, 280, 600)
    RECT_MENSAGEM = (X0 + 16, Y0 + 606, RECT_PLANO[2], 58)

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
