"""
PARTE 1 — Gerador do plano cartesiano e dos pontos de partida e chegada

* PlanoCartesiano: converte coordenadas do plano (x, y) <-> pixels da tela
  e desenha a grade, os eixos x e y, as setas e a numeração.
* gerar_pontos_da_pista: sorteia o ponto de chegada C e define os dois pontos
  de partida A e B na linha de largada. A e B ficam simétricos em relação à
  reta horizontal que passa por C, então d(A, C) = d(B, C): a corrida é justa.
"""
import math

import pygame

import config
from geometria import Vetor
from parte9_visual import Cores, fonte, texto, rotulo, linha_tracejada, brilho, bandeira_quadriculada


class PlanoCartesiano:
    def __init__(self, rect_tela, xmin, xmax, ymin, ymax):
        self.rect = pygame.Rect(rect_tela)
        self.xmin, self.xmax = xmin, xmax
        self.ymin, self.ymax = ymin, ymax
        self.escala = min(self.rect.width / (xmax - xmin), self.rect.height / (ymax - ymin))
        self.deslocamento = (0, 0)  # usado pelo tremor de tela
        self._grade = None

    # ------------------------------------------------ Conversões ----
    def para_tela(self, p):
        """(x, y) do plano -> (px, py) da tela. O eixo y da tela cresce para BAIXO,
        por isso o y é invertido:  py = base - (y - ymin) * escala."""
        dx, dy = self.deslocamento
        return (self.rect.left + (p.x - self.xmin) * self.escala + dx,
                self.rect.bottom - (p.y - self.ymin) * self.escala + dy)

    def para_plano(self, pixel):
        """(px, py) da tela -> (x, y) do plano (inversa de para_tela)."""
        px, py = pixel
        return Vetor(self.xmin + (px - self.rect.left) / self.escala,
                     self.ymin + (self.rect.bottom - py) / self.escala)

    def contem(self, p, margem=0.0):
        return (self.xmin + margem <= p.x <= self.xmax - margem and
                self.ymin + margem <= p.y <= self.ymax - margem)

    # ------------------------------------------------ Desenho ----
    def _criar_grade(self):
        sup = pygame.Surface(self.rect.size)
        sup.fill(Cores.PLANO)

        def local(x, y):
            return ((x - self.xmin) * self.escala, self.rect.height - (y - self.ymin) * self.escala)

        for x in range(math.ceil(self.xmin), math.floor(self.xmax) + 1):
            cor = Cores.GRADE_GROSSA if x % 2 == 0 else Cores.GRADE_FINA
            pygame.draw.line(sup, cor, local(x, self.ymin), local(x, self.ymax))
        for y in range(math.ceil(self.ymin), math.floor(self.ymax) + 1):
            cor = Cores.GRADE_GROSSA if y % 2 == 0 else Cores.GRADE_FINA
            pygame.draw.line(sup, cor, local(self.xmin, y), local(self.xmax, y))

        # Eixos com setas
        ox, oy = local(0, 0)
        fim_x = local(self.xmax, 0)
        fim_y = local(0, self.ymax)
        pygame.draw.line(sup, Cores.EIXOS, local(self.xmin, 0), fim_x, 2)
        pygame.draw.line(sup, Cores.EIXOS, local(0, self.ymin), fim_y, 2)
        pygame.draw.polygon(sup, Cores.EIXOS, [fim_x, (fim_x[0] - 12, fim_x[1] - 6), (fim_x[0] - 12, fim_x[1] + 6)])
        pygame.draw.polygon(sup, Cores.EIXOS, [fim_y, (fim_y[0] - 6, fim_y[1] + 12), (fim_y[0] + 6, fim_y[1] + 12)])
        texto(sup, "x", (fim_x[0] - 8, fim_x[1] + 8), 18, Cores.EIXOS, True, "midtop")
        texto(sup, "y", (fim_y[0] + 12, fim_y[1] + 2), 18, Cores.EIXOS, True, "topleft")
        texto(sup, "O", (ox - 5, oy + 3), 13, Cores.EIXOS, True, "topright")

        # Numeração de 2 em 2
        for x in range(math.ceil(self.xmin) + 1, math.floor(self.xmax)):
            if x != 0 and x % 2 == 0:
                px, py = local(x, 0)
                pygame.draw.line(sup, Cores.EIXOS, (px, py - 4), (px, py + 4), 2)
                texto(sup, x, (px, py + 5), 12, Cores.TEXTO_SUAVE, False, "midtop")
        for y in range(math.ceil(self.ymin) + 1, math.floor(self.ymax)):
            if y != 0 and y % 2 == 0:
                px, py = local(0, y)
                pygame.draw.line(sup, Cores.EIXOS, (px - 4, py), (px + 4, py), 2)
                texto(sup, y, (px - 7, py), 12, Cores.TEXTO_SUAVE, False, "midright")

        pygame.draw.rect(sup, Cores.PAINEL_BORDA, sup.get_rect(), 2)
        return sup

    def desenhar(self, superficie):
        if self._grade is None:
            self._grade = self._criar_grade()
        dx, dy = self.deslocamento
        superficie.blit(self._grade, (self.rect.left + dx, self.rect.top + dy))


class Pista:
    """Pontos de partida (um por jogador) e o ponto de chegada comum."""

    def __init__(self, partidas, chegada, raio_chegada):
        self.partidas = partidas
        self.chegada = chegada
        self.raio_chegada = raio_chegada


def gerar_pontos_da_pista(rng):
    # y da chegada sorteado em passos de 0.5 para dar coordenadas "bonitas"
    yc = round(rng.uniform(-config.FAIXA_Y_CHEGADA, config.FAIXA_Y_CHEGADA) * 2) / 2
    chegada = Vetor(config.X_CHEGADA, yc)
    partidas = [Vetor(config.X_PARTIDA, yc + config.SEPARACAO_PARTIDAS),
                Vetor(config.X_PARTIDA, yc - config.SEPARACAO_PARTIDAS)]
    return Pista(partidas, chegada, config.RAIO_CHEGADA)


def desenhar_pista(superficie, plano, pista, cores_jogadores, tempo):
    # Linha de largada: reta vertical x = X_PARTIDA
    ys = [p.y for p in pista.partidas]
    topo = plano.para_tela(Vetor(config.X_PARTIDA, max(ys) + 1.3))
    base = plano.para_tela(Vetor(config.X_PARTIDA, min(ys) - 1.3))
    linha_tracejada(superficie, Cores.TEXTO_SUAVE, base, topo, 2, 7, 5)
    img = pygame.transform.rotate(fonte(13, True).render("LARGADA", True, Cores.TEXTO_SUAVE), 90)
    superficie.blit(img, img.get_rect(midright=(topo[0] - 6, (topo[1] + base[1]) / 2)))

    # Pontos de partida A e B
    for nome, p, cor in zip("AB", pista.partidas, cores_jogadores):
        pt = plano.para_tela(p)
        pygame.draw.circle(superficie, cor, pt, 15, 2)
        rotulo(superficie, f"{nome}{p.formatar(1)}", (pt[0] + 8, pt[1] - 26), cor, tamanho=12)

    # Ponto de chegada C
    ct = plano.para_tela(pista.chegada)
    r = pista.raio_chegada * plano.escala
    brilho(superficie, ct, r * (2.2 + 0.25 * math.sin(tempo * 3)), Cores.DESTAQUE, 110)
    bandeira_quadriculada(superficie, ct, r)
    pygame.draw.circle(superficie, Cores.DESTAQUE, ct, r, 3)
    rotulo(superficie, f"C{pista.chegada.formatar(1)}", (ct[0] - 4, ct[1] - r - 16), Cores.DESTAQUE, tamanho=12)
    rotulo(superficie, "CHEGADA", (ct[0] - 4, ct[1] + r + 14), Cores.DESTAQUE, tamanho=12)
