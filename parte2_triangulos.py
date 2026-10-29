"""
PARTE 2 — Gerador de obstáculos TRIANGULARES

Os triângulos são "previamente definidos" (3 pontos cada) e "escolhidos
aleatoriamente": a cada partida sorteamos QUAL molde usar, ONDE colocar
(translação) e com que ângulo girar (matriz de rotação).

Antes de aceitar um triângulo, testamos posicao_e_valida (obstaculo.py):
ele precisa ficar a uma distância mínima dos outros obstáculos e dos pontos
de partida e chegada, para não bloquear 100% a pista.
"""
import math

from obstaculo import construir_obstaculo, posicao_e_valida, sortear_centro

# Moldes: vértices (x, y) em torno da origem. 1 unidade = 1 quadradinho do plano.
TRIANGULOS_PREDEFINIDOS = [
    ("Triângulo Equilátero",   [(0.0, 1.3), (-1.126, -0.65), (1.126, -0.65)]),
    ("Triângulo Retângulo",    [(-0.9, -0.8), (1.3, -0.8), (-0.9, 1.0)]),
    ("Triângulo Isósceles",    [(0.0, 1.5), (-0.8, -0.9), (0.8, -0.9)]),
    ("Triângulo Escaleno",     [(-1.2, -0.6), (1.4, -0.3), (-0.2, 1.1)]),
    ("Triângulo Obtusângulo",  [(-1.5, -0.4), (1.5, -0.4), (0.4, 0.6)]),
]


def gerar_triangulos(quantidade, obstaculos_existentes, pontos_protegidos, rng, tentativas=400):
    """Devolve uma lista com até 'quantidade' triângulos bem espaçados."""
    novos = []
    for _ in range(quantidade):
        for _ in range(tentativas):
            nome, molde = rng.choice(TRIANGULOS_PREDEFINIDOS)
            angulo = rng.uniform(0, 2 * math.pi)
            triangulo = construir_obstaculo("triangulo", nome, molde, sortear_centro(rng), angulo)
            if posicao_e_valida(triangulo, obstaculos_existentes + novos, pontos_protegidos):
                novos.append(triangulo)
                break
    return novos
