"""
obstaculo.py — Base comum das PARTES 2 e 3 (triângulos e quadrados).

Um obstáculo é um polígono convexo dado pelos seus vértices.
Aqui ficam:
  * a classe Obstaculo (teste de ponto dentro, distância, colisão com segmento)
  * construir_obstaculo: leva um "molde" pré-definido até o lugar sorteado
    usando rotação + translação:  V_final = centro + R(θ) · V_molde
  * posicao_e_valida: a regra de distância mínima entre obstáculos e até os
    pontos de partida/chegada, para a pista NUNCA ficar 100% bloqueada.

Por que a pista nunca fica bloqueada?
  Cada obstáculo cabe dentro do seu círculo circunscrito (centro = baricentro,
  raio = maior distância até um vértice). Exigimos que dois círculos fiquem a
  pelo menos DIST_MIN_ENTRE_OBSTACULOS um do outro e das bordas de cima/baixo.
  Essa folga é maior que o diâmetro do marcador (2 · RAIO_JOGADOR), então
  sempre existe um "corredor" entre quaisquer dois obstáculos.
"""
import pygame

import config
from geometria import (Vetor, centroide, distancia, rotacionar, ponto_no_poligono_convexo,
                       distancia_ponto_segmento, distancia_entre_segmentos)
from parte9_visual import Cores, misturar, rotulo


class Obstaculo:
    def __init__(self, tipo, nome, vertices):
        self.tipo = tipo          # "triangulo" ou "quadrado"
        self.nome = nome
        self.vertices = vertices  # lista de Vetor
        self.centro = centroide(vertices)
        self.raio = max(distancia(self.centro, v) for v in vertices)  # raio circunscrito

    def arestas(self):
        n = len(self.vertices)
        return [(self.vertices[i], self.vertices[(i + 1) % n]) for i in range(n)]

    def contem(self, p):
        return ponto_no_poligono_convexo(p, self.vertices)

    def distancia_ate_ponto(self, p):
        if self.contem(p):
            return 0.0
        return min(distancia_ponto_segmento(p, a, b) for a, b in self.arestas())

    def colide_com_segmento(self, a, b, folga=0.0):
        """O segmento AB passa a menos de 'folga' do obstáculo?"""
        # Teste rápido: se o segmento está longe do círculo circunscrito, não colide.
        if distancia_ponto_segmento(self.centro, a, b) > self.raio + folga:
            return False
        if self.contem(a) or self.contem(b):
            return True
        return any(distancia_entre_segmentos(a, b, p, q) <= folga for p, q in self.arestas())


def construir_obstaculo(tipo, nome, molde, centro, angulo):
    """Aplica rotação R(θ) e translação ao molde (lista de pares (x, y) em torno da origem)."""
    vertices = [centro + rotacionar(Vetor(x, y), angulo) for x, y in molde]
    return Obstaculo(tipo, nome, vertices)


def posicao_e_valida(novo, existentes, pontos_protegidos):
    c, r = novo.centro, novo.raio

    # 1) Dentro da faixa permitida (longe da largada/chegada e das bordas)
    if c.x - r < config.OBST_XMIN or c.x + r > config.OBST_XMAX:
        return False
    if c.y - r < config.PLANO_YMIN + config.MARGEM_BORDA or c.y + r > config.PLANO_YMAX - config.MARGEM_BORDA:
        return False

    # 2) Longe dos outros obstáculos: d(C1, C2) >= r1 + r2 + folga
    for outro in existentes:
        if distancia(c, outro.centro) < r + outro.raio + config.DIST_MIN_ENTRE_OBSTACULOS:
            return False

    # 3) Longe dos pontos de partida e de chegada
    for p in pontos_protegidos:
        if distancia(c, p) < r + config.DIST_MIN_DOS_PONTOS:
            return False
    return True


def sortear_centro(rng):
    return Vetor(rng.uniform(config.OBST_XMIN, config.OBST_XMAX),
                 rng.uniform(config.PLANO_YMIN, config.PLANO_YMAX))


def desenhar_obstaculo(superficie, plano, obstaculo, destacado=False, mostrar_vertices=False):
    cor = Cores.TRIANGULO if obstaculo.tipo == "triangulo" else Cores.QUADRADO
    pontos = [plano.para_tela(v) for v in obstaculo.vertices]
    sombra = [(x + 4, y + 5) for x, y in pontos]

    pygame.draw.polygon(superficie, misturar(cor, Cores.PRETO, 0.75), sombra)
    pygame.draw.polygon(superficie, misturar(cor, Cores.PLANO, 0.55 if not destacado else 0.3), pontos)
    pygame.draw.polygon(superficie, misturar(cor, Cores.BRANCO, 0.35 if destacado else 0.0), pontos, 3)
    for p in pontos:
        pygame.draw.circle(superficie, Cores.BRANCO if destacado else cor, p, 4)

    if destacado or mostrar_vertices:
        for v, p in zip(obstaculo.vertices, pontos):
            dx = 1 if p[0] >= plano.para_tela(obstaculo.centro)[0] else -1
            dy = 1 if p[1] >= plano.para_tela(obstaculo.centro)[1] else -1
            rotulo(superficie, v.formatar(1), (p[0] + dx * 30, p[1] + dy * 12), cor, tamanho=11)
    if destacado:
        rotulo(superficie, obstaculo.nome, plano.para_tela(obstaculo.centro), Cores.TEXTO, tamanho=12)
