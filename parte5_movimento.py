"""
PARTE 5 — Executar e validar o movimento

O movimento é o SEGMENTO de reta que vai da posição atual O até o destino D:
      P(t) = O + t·(D - O),   0 <= t <= 1

Validação, na ordem:
  1. D está dentro do setor circular sorteado (parte 4)?   senão: jogada inválida
  2. D está dentro do plano cartesiano?                     senão: jogada inválida
  3. O segmento OD passa a menos de RAIO_JOGADOR de algum obstáculo?  -> COLISÃO
     (distância entre segmentos via determinantes e projeção ortogonal)
  4. O segmento toca o círculo de chegada?                              -> CHEGADA
     Resolve a equação do 2º grau  |O + t·d - C|² = r²  em t.
  5. Caso contrário o movimento é NORMAL e o jogador vai para D.
"""
import math

import config
from geometria import produto_escalar

NORMAL, COLISAO, CHEGADA, INVALIDO = "normal", "colisao", "chegada", "invalido"


class ResultadoMovimento:
    def __init__(self, tipo, origem, destino, mensagem, ponto_impacto=None, obstaculo=None):
        self.tipo = tipo
        self.origem = origem
        self.destino = destino            # onde o jogador termina a jogada
        self.mensagem = mensagem
        self.ponto_impacto = ponto_impacto
        self.obstaculo = obstaculo

    @property
    def valido(self):
        return self.tipo != INVALIDO


def instante_de_chegada(origem, destino, chegada, raio):
    """Menor t em [0, 1] com |O + t·d - C| = r, ou None se o segmento não toca o círculo.
    Expandindo:  (d·d) t² + 2 (d·w) t + (w·w - r²) = 0,  com d = D - O e w = O - C."""
    d = destino - origem
    w = origem - chegada
    a = produto_escalar(d, d)
    b = 2 * produto_escalar(d, w)
    c = produto_escalar(w, w) - raio ** 2
    if c <= 0:
        return 0.0  # já começou dentro do círculo
    if a == 0:
        return None
    delta = b * b - 4 * a * c
    if delta < 0:
        return None
    t = (-b - math.sqrt(delta)) / (2 * a)
    return t if 0 <= t <= 1 else None


def instante_do_impacto(origem, destino, obstaculo, folga, passos=300):
    """Percorre o segmento e devolve o primeiro t em que o marcador encosta no obstáculo
    (usado para animar a batida exatamente no ponto certo)."""
    d = destino - origem
    melhor_t, menor = 1.0, float("inf")
    for i in range(passos + 1):
        t = i / passos
        dist = obstaculo.distancia_ate_ponto(origem + d * t)
        if dist <= folga:
            return t
        if dist < menor:
            menor, melhor_t = dist, t
    return melhor_t


def validar_movimento(origem, destino, setor, plano, obstaculos, pista):
    # 1) Regra do setor circular
    if not setor.contem(destino):
        return ResultadoMovimento(INVALIDO, origem, origem,
                                  "Jogada inválida: o destino está fora do setor circular.")
    # 2) Dentro do plano
    if not plano.contem(destino, config.RAIO_JOGADOR):
        return ResultadoMovimento(INVALIDO, origem, origem,
                                  "Jogada inválida: o destino está fora do plano cartesiano.")

    # 3) Colisão com obstáculos (fica com a batida que acontece primeiro)
    impacto = None
    for obst in obstaculos:
        if obst.colide_com_segmento(origem, destino, config.RAIO_JOGADOR):
            t = instante_do_impacto(origem, destino, obst, config.RAIO_JOGADOR)
            if impacto is None or t < impacto[0]:
                impacto = (t, obst)

    # 4) Chegada (vale se acontecer ANTES de uma eventual batida)
    t_chegada = instante_de_chegada(origem, destino, pista.chegada, pista.raio_chegada)
    if t_chegada is not None and (impacto is None or t_chegada < impacto[0]):
        return ResultadoMovimento(CHEGADA, origem, pista.chegada, "Chegou ao ponto final!")

    if impacto is not None:
        t, obst = impacto
        ponto = origem + (destino - origem) * t
        return ResultadoMovimento(COLISAO, origem, origem, f"Bateu no {obst.nome}!", ponto, obst)

    # 5) Movimento normal
    return ResultadoMovimento(NORMAL, origem, destino, "Movimento válido.")


def existe_jogada_valida(setor, plano, obstaculos, amostras_r=5, amostras_ang=12):
    """Testa uma 'malha' de pontos do setor para garantir que o jogador tenha
    pelo menos uma jogada sem batida andando de R/2 até R (senão o setor é sorteado de novo)."""
    for i in range(amostras_r):
        r = setor.raio * (0.5 + 0.5 * i / (amostras_r - 1))
        for j in range(amostras_ang + 1):
            destino = setor.ponto(r, setor.theta_inicial + setor.abertura * j / amostras_ang)
            if not plano.contem(destino, config.RAIO_JOGADOR):
                continue
            if not any(o.colide_com_segmento(setor.centro, destino, config.RAIO_JOGADOR) for o in obstaculos):
                return True
    return False
