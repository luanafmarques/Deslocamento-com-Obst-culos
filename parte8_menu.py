"""
PARTE 8 — Interface gráfica do menu inicial

Tela de abertura com:
  * título e fundo animado (os mesmos triângulos e quadrados do jogo
    flutuando e girando com a matriz de rotação)
  * botões: Jogar, Dificuldade (alterna Fácil/Médio/Difícil), Como jogar, Sair
  * painel "Como jogar" com as regras
"""
import math
import random

import pygame

import config
from geometria import Vetor, rotacionar
from parte2_triangulos import TRIANGULOS_PREDEFINIDOS
from parte3_quadrados import QUADRADOS_PREDEFINIDOS
from parte9_visual import (Cores, Botao, texto, texto_com_sombra, painel, desenhar_fundo,
                           escurecer_tela, desenhar_jogador, misturar)

REGRAS = [
    ("OBJETIVO", Cores.DESTAQUE, [
        "Levar seu marcador da largada até a chegada (bandeira quadriculada) antes do adversário.",
    ]),
    ("A CADA JOGADA", Cores.VALIDO, [
        "Um setor circular é sorteado a partir da sua posição, com raio R e abertura α.",
        "Escolha um destino DENTRO do setor e confirme. O movimento é o segmento de reta",
        "entre a sua posição atual e o destino escolhido.",
    ]),
    ("BATIDAS", Cores.INVALIDO, [
        "Se o segmento encostar em um triângulo ou quadrado, você bate:",
        "volta para onde estava e perde a próxima vez.",
    ]),
    ("VITÓRIA", Cores.JOGADOR_1, [
        "Quem tocar o círculo de chegada vence. A rodada sempre termina, então se os",
        "dois chegarem na mesma rodada dá empate.",
    ]),
    ("CONTROLES", Cores.JOGADOR_2, [
        "Mouse: mirar  |  Clique: jogar  |  Setas: ajuste fino (Shift = mais rápido)",
        "Enter/Espaço: confirmar  |  V: mostrar vértices  |  Esc: voltar ao menu",
    ]),
]


class FormaFlutuante:
    """Triângulo/quadrado decorativo do fundo do menu."""

    def __init__(self, rng):
        if rng.random() < 0.5:
            self.molde = rng.choice(TRIANGULOS_PREDEFINIDOS)[1]
            self.cor = Cores.TRIANGULO
        else:
            self.molde = rng.choice(QUADRADOS_PREDEFINIDOS)[1]
            self.cor = Cores.QUADRADO
        self.escala = rng.uniform(18, 42)
        self.pos = Vetor(rng.uniform(0, config.LARGURA), rng.uniform(0, config.ALTURA))
        self.vel = Vetor(rng.uniform(-25, 25), rng.uniform(-25, 25))
        self.angulo = rng.uniform(0, 2 * math.pi)
        self.giro = rng.uniform(-0.8, 0.8)

    def atualizar(self, dt):
        self.pos = self.pos + self.vel * dt
        self.angulo += self.giro * dt
        margem = 60
        if self.pos.x < -margem: self.pos.x = config.LARGURA + margem
        if self.pos.x > config.LARGURA + margem: self.pos.x = -margem
        if self.pos.y < -margem: self.pos.y = config.ALTURA + margem
        if self.pos.y > config.ALTURA + margem: self.pos.y = -margem

    def desenhar(self, camada):
        pontos = [tuple(self.pos + rotacionar(Vetor(x, y) * self.escala, self.angulo)) for x, y in self.molde]
        pygame.draw.polygon(camada, (*self.cor, 28), pontos)
        pygame.draw.polygon(camada, (*self.cor, 90), pontos, 2)


class Menu:
    def __init__(self, dificuldade=config.DIFICULDADE_PADRAO):
        self.dificuldade = dificuldade
        self.tempo = 0.0
        self.mostrando_regras = False
        rng = random.Random()
        self.formas = [FormaFlutuante(rng) for _ in range(18)]

        cx = config.LARGURA // 2
        largura, altura, y0 = 340, 54, 300
        self.botoes = [
            Botao((cx - largura // 2, y0, largura, altura), "Jogar", "jogar", Cores.VALIDO, 24),
            Botao((cx - largura // 2, y0 + 70, largura, altura), "", "dificuldade", Cores.DESTAQUE),
            Botao((cx - largura // 2, y0 + 140, largura, altura), "Como jogar", "regras", Cores.JOGADOR_1),
            Botao((cx - largura // 2, y0 + 210, largura, altura), "Sair", "sair", Cores.INVALIDO),
        ]
        self._atualizar_rotulo_dificuldade()
        self.botao_voltar = Botao((cx - 120, config.ALTURA - 96, 240, 50), "Voltar", "voltar", Cores.JOGADOR_1)

    def _atualizar_rotulo_dificuldade(self):
        self.botoes[1].rotulo = f"Dificuldade: {self.dificuldade}"

    # ------------------------------------------------ Eventos ----
    def tratar_evento(self, evento):
        """Devolve 'jogar', 'sair' ou None."""
        if self.mostrando_regras:
            if self.botao_voltar.clicado(evento) or (evento.type == pygame.KEYDOWN and
                                                     evento.key in (pygame.K_ESCAPE, pygame.K_RETURN)):
                self.mostrando_regras = False
            return None

        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            return "jogar"
        for botao in self.botoes:
            if botao.clicado(evento):
                if botao.acao == "dificuldade":
                    ordem = config.ORDEM_DIFICULDADES
                    self.dificuldade = ordem[(ordem.index(self.dificuldade) + 1) % len(ordem)]
                    self._atualizar_rotulo_dificuldade()
                elif botao.acao == "regras":
                    self.mostrando_regras = True
                else:
                    return botao.acao
        return None

    def atualizar(self, dt):
        self.tempo += dt
        for forma in self.formas:
            forma.atualizar(dt)

    # ------------------------------------------------ Desenho ----
    def desenhar(self, tela):
        desenhar_fundo(tela)
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for forma in self.formas:
            forma.desenhar(camada)
        tela.blit(camada, (0, 0))

        if self.mostrando_regras:
            self._desenhar_regras(tela)
            return

        cx = config.LARGURA // 2
        flutuar = 6 * math.sin(self.tempo * 1.6)
        texto_com_sombra(tela, "DESLOCAMENTO", (cx, 120 + flutuar), 64, Cores.DESTAQUE)
        texto_com_sombra(tela, "COM OBSTÁCULOS", (cx, 186 + flutuar), 40, Cores.TEXTO)
        texto(tela, "Trabalho de GAAL  ·  Geometria Analítica e Álgebra Linear",
              (cx, 236), 17, Cores.TEXTO_SUAVE, False, "center")

        # Os dois competidores enfeitando o título
        desenhar_jogador(tela, (cx - 300, 152 + flutuar), Cores.JOGADOR_1, 1, 16, True, self.tempo)
        desenhar_jogador(tela, (cx + 300, 152 - flutuar), Cores.JOGADOR_2, 2, 16, True, self.tempo + 1)

        for botao in self.botoes:
            botao.desenhar(tela)
        texto(tela, "Enter para jogar", (cx, config.ALTURA - 28), 14, Cores.TEXTO_SUAVE, False, "center")

    def _desenhar_regras(self, tela):
        escurecer_tela(tela, 120)
        rect = pygame.Rect(0, 0, 820, 520)
        rect.center = (config.LARGURA // 2, config.ALTURA // 2 - 30)
        painel(tela, rect)
        texto(tela, "COMO JOGAR", (rect.centerx, rect.top + 34), 30, Cores.DESTAQUE, True, "center")
        y = rect.top + 70
        for titulo, cor, linhas in REGRAS:
            pygame.draw.rect(tela, cor, (rect.left + 34, y + 4, 6, 18), border_radius=3)
            texto(tela, titulo, (rect.left + 50, y), 17, cor, True)
            y += 26
            for linha in linhas:
                texto(tela, linha, (rect.left + 50, y), 15, misturar(Cores.TEXTO, Cores.TEXTO_SUAVE, 0.2))
                y += 21
            y += 10
        self.botao_voltar.desenhar(tela)
