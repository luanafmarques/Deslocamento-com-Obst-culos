"""
PARTE 3 — Gerador de obstáculos QUADRADOS

Mesma ideia da parte 2, mas com quadrados (4 pontos). Os moldes têm lados
diferentes; a rotação sorteada faz alguns aparecerem "em pé" e outros
inclinados (como losangos), mas continuam sendo quadrados: a rotação é uma
transformação linear que preserva distâncias e ângulos.

A regra de espaçamento é a mesma (posicao_e_valida em obstaculo.py).
"""
import math

from obstaculo import construir_obstaculo, posicao_e_valida, sortear_centro

# Moldes: 4 vértices (x, y) em torno da origem, no sentido anti-horário.
QUADRADOS_PREDEFINIDOS = [
    ("Quadrado Pequeno (lado 1.4)", [(-0.7, -0.7), (0.7, -0.7), (0.7, 0.7), (-0.7, 0.7)]),
    ("Quadrado Médio (lado 1.8)",   [(-0.9, -0.9), (0.9, -0.9), (0.9, 0.9), (-0.9, 0.9)]),
    ("Quadrado Grande (lado 2.2)",  [(-1.1, -1.1), (1.1, -1.1), (1.1, 1.1), (-1.1, 1.1)]),
]

# Ângulos possíveis de rotação (em graus)
ANGULOS_QUADRADO = [0, 15, 30, 45, 60, 75]


def gerar_quadrados(quantidade, obstaculos_existentes, pontos_protegidos, rng, tentativas=400):
    """Devolve uma lista com até 'quantidade' quadrados bem espaçados."""
    novos = []
    for _ in range(quantidade):
        for _ in range(tentativas):
            nome, molde = rng.choice(QUADRADOS_PREDEFINIDOS)
            angulo = math.radians(rng.choice(ANGULOS_QUADRADO))
            quadrado = construir_obstaculo("quadrado", nome, molde, sortear_centro(rng), angulo)
            if posicao_e_valida(quadrado, obstaculos_existentes + novos, pontos_protegidos):
                novos.append(quadrado)
                break
    return novos
