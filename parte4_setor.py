"""
PARTE 4 — Ponto inicial da jogada e o SETOR CIRCULAR de movimentos possíveis

A cada jogada sorteamos um setor circular com centro na posição atual P do
jogador:
  * raio R           -> distância máxima que ele pode andar
  * direção φ        -> para onde o setor "aponta" (perto da direção da chegada)
  * abertura α       -> ângulo total do setor (vai de φ - α/2 até φ + α/2)

Um ponto Q pertence ao setor quando, com v = Q - P:
      |v| <= R          (está dentro do círculo de raio R)
  e   ângulo(v, u) <= α/2,  onde u = (cos φ, sin φ)
O ângulo é calculado pelo produto escalar: cos(ângulo) = (v·u) / (|v||u|).

O setor é desenhado no plano com o raio R e o ângulo α escritos nele.
"""
import math

import pygame

from geometria import (Vetor, norma, vetor_polar, angulo_entre, angulo_do_vetor, normalizar_angulo)
from parte9_visual import Cores, rotulo, linha_tracejada, misturar


class SetorCircular:
    def __init__(self, centro, raio, direcao, abertura):
        self.centro = centro      # Vetor P (posição do jogador)
        self.raio = raio          # R
        self.direcao = direcao    # φ (radianos)
        self.abertura = abertura  # α (radianos)

    @property
    def theta_inicial(self):
        return self.direcao - self.abertura / 2

    @property
    def theta_final(self):
        return self.direcao + self.abertura / 2

    def contem(self, q):
        v = q - self.centro
        d = norma(v)
        if d < 1e-6 or d > self.raio + 1e-6:
            return False
        u = vetor_polar(1, self.direcao)
        return angulo_entre(v, u) <= self.abertura / 2 + 1e-6

    def ponto(self, r, theta):
        """Ponto do plano dado em coordenadas polares a partir do centro: P + (r cos θ, r sin θ)."""
        return self.centro + vetor_polar(r, theta)

    def polar_de(self, q):
        """(r, θ) do ponto Q em relação ao centro. θ é dado perto de φ (sem 'pular' 360°)."""
        v = q - self.centro
        theta = self.direcao + normalizar_angulo(angulo_do_vetor(v) - self.direcao)
        return norma(v), theta

    def limitar(self, r, theta):
        """Prende (r, θ) dentro do setor (usado na mira pelo teclado)."""
        r = max(0.1, min(self.raio, r))
        desvio = normalizar_angulo(theta - self.direcao)
        desvio = max(-self.abertura / 2, min(self.abertura / 2, desvio))
        return r, self.direcao + desvio

    def pontos_do_arco(self, r, n=48):
        return [self.ponto(r, self.theta_inicial + self.abertura * k / n) for k in range(n + 1)]


def gerar_setor(posicao, alvo, rng, dificuldade, desvio_max=None):
    """Sorteia R, α e φ. φ = direção do vetor (alvo - posição) ± um desvio aleatório."""
    if desvio_max is None:
        desvio_max = dificuldade["desvio"]
    raio = rng.uniform(*dificuldade["raio"])
    abertura = math.radians(rng.uniform(*dificuldade["abertura"]))
    rumo = angulo_do_vetor(alvo - posicao)
    direcao = rumo + math.radians(rng.uniform(-desvio_max, desvio_max))
    return SetorCircular(posicao, raio, direcao, abertura)


def desenhar_setor(superficie, plano, setor, cor, tempo):
    centro = plano.para_tela(setor.centro)
    contorno = [centro] + [plano.para_tela(p) for p in setor.pontos_do_arco(setor.raio)]

    superficie.set_clip(plano.rect)

    # Preenchimento translúcido "respirando" + anéis de 1 em 1 unidade.
    # A camada transparente tem só o tamanho do setor (bem mais leve no navegador).
    x0 = int(min(x for x, _ in contorno)) - 2
    y0 = int(min(y for _, y in contorno)) - 2
    largura = int(max(x for x, _ in contorno)) - x0 + 4
    altura = int(max(y for _, y in contorno)) - y0 + 4

    def local(pontos):
        return [(x - x0, y - y0) for x, y in pontos]

    camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
    alpha = int(50 + 18 * math.sin(tempo * 3))
    pygame.draw.polygon(camada, (*cor, alpha), local(contorno))
    anel = 1
    while anel < setor.raio:
        arco = [plano.para_tela(p) for p in setor.pontos_do_arco(anel, 32)]
        pygame.draw.lines(camada, (*cor, 90), False, local(arco), 1)
        anel += 1
    superficie.blit(camada, (x0, y0))

    # Borda do setor
    pygame.draw.lines(superficie, cor, True, contorno, 2)

    # Bissetriz (direção φ) tracejada
    linha_tracejada(superficie, misturar(cor, Cores.PLANO, 0.35), centro,
                    plano.para_tela(setor.ponto(setor.raio, setor.direcao)), 1, 6, 6)

    # Arco do ângulo α perto do centro
    r_arco = min(1.0, setor.raio * 0.35)
    pygame.draw.lines(superficie, Cores.DESTAQUE, False,
                      [plano.para_tela(p) for p in setor.pontos_do_arco(r_arco, 24)], 2)

    # Rótulos: raio R (no meio de um dos lados) e ângulo α
    lado = setor.theta_final
    meio_lado = setor.ponto(setor.raio / 2, lado) + vetor_polar(0.45, lado + math.pi / 2)
    rotulo(superficie, f"R = {setor.raio:.2f}", plano.para_tela(meio_lado), cor, tamanho=13)
    pos_alfa = setor.ponto(r_arco + 0.6, setor.direcao)
    rotulo(superficie, f"α = {math.degrees(setor.abertura):.0f}°", plano.para_tela(pos_alfa), Cores.DESTAQUE, tamanho=13)

    superficie.set_clip(None)
