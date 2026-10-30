"""
PARTE 8 — Interface gráfica do menu inicial

Tela de abertura com:
  * título e fundo animado (os mesmos triângulos e quadrados do jogo
    flutuando e girando com a matriz de rotação)
  * botões: Jogar, Dificuldade (alterna Fácil/Médio/Difícil), Como jogar
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
        "Celular: toque para mirar (ou arraste) e toque de novo no destino ou em \"Confirmar jogada\"",
    ]),
]


# Versão curta das regras para a tela do celular (em duas colunas)
REGRAS_CELULAR = [
    [("OBJETIVO", Cores.DESTAQUE, ["Chegar à bandeira antes do adversário."]),
     ("A CADA JOGADA", Cores.VALIDO, ["Um setor (raio R, ângulo α) mostra",
                                      "até onde você pode ir. O movimento",
                                      "é um segmento de reta."])],
    [("BATIDAS", Cores.INVALIDO, ["Encostou num obstáculo? Volta para",
                                  "onde estava e perde a próxima vez."]),
     ("VITÓRIA", Cores.JOGADOR_1, ["Tocou a chegada, venceu. Se os dois",
                                   "chegarem na mesma rodada, empate."]),
     ("TOQUE", Cores.JOGADOR_2, ["Toque para mirar. Toque de novo no",
                                 "destino (ou em Confirmar) para jogar."])],
]

FUNDO_MEDIO = misturar(Cores.FUNDO_TOPO, Cores.FUNDO_BASE, 0.5)


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

    def desenhar(self, tela):
        # Cores "apagadas" já misturadas com o fundo: dá o efeito de transparência
        # sem precisar de camada transparente (bem mais leve no navegador).
        pontos = [tuple(self.pos + rotacionar(Vetor(x, y) * self.escala, self.angulo)) for x, y in self.molde]
        pygame.draw.polygon(tela, misturar(self.cor, FUNDO_MEDIO, 0.88), pontos)
        pygame.draw.polygon(tela, misturar(self.cor, FUNDO_MEDIO, 0.6), pontos, 2)


class Menu:
    def __init__(self, dificuldade=config.DIFICULDADE_PADRAO):
        self.dificuldade = dificuldade
        self.tempo = 0.0
        self.mostrando_regras = False
        rng = random.Random()
        self.formas = [FormaFlutuante(rng) for _ in range(18)]

        cx = config.LARGURA // 2
        if config.CELULAR:
            largura, altura, y0, passo = 320, 50, 190, 62
        else:
            largura, altura, y0, passo = 340, 54, config.Y0 + 340, 70
        self.botoes = [
            Botao((cx - largura // 2, y0, largura, altura), "Jogar", "jogar", Cores.VALIDO, 24),
            Botao((cx - largura // 2, y0 + passo, largura, altura), "", "dificuldade", Cores.DESTAQUE),
            Botao((cx - largura // 2, y0 + 2 * passo, largura, altura), "Como jogar", "regras", Cores.JOGADOR_1),
        ]
        self._atualizar_rotulo_dificuldade()
        voltar_y = config.ALTURA - (62 if config.CELULAR else 96)
        self.botao_voltar = Botao((cx - 120, voltar_y, 240, 50), "Voltar", "voltar", Cores.JOGADOR_1)

    def _atualizar_rotulo_dificuldade(self):
        self.botoes[1].rotulo = f"Dificuldade: {self.dificuldade}"

    # ------------------------------------------------ Eventos ----
    def tratar_evento(self, evento):
        """Devolve 'jogar' ou None."""
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
        for forma in self.formas:
            forma.desenhar(tela)

        if self.mostrando_regras:
            self._desenhar_regras(tela)
            return

        cx = config.LARGURA // 2
        flutuar = 6 * math.sin(self.tempo * 1.6)
        if config.CELULAR:  # (y do título, y do subtítulo, y dos créditos, tamanhos, distância dos marcadores)
            y1, y2, y3, t1, t2, dx = 58, 112, 152, 52, 32, 250
        else:
            topo = config.Y0 + 20
            y1, y2, y3, t1, t2, dx = topo + 120, topo + 186, topo + 236, 64, 40, 300
        texto_com_sombra(tela, "DESLOCAMENTO", (cx, y1 + flutuar), t1, Cores.DESTAQUE)
        texto_com_sombra(tela, "COM OBSTÁCULOS", (cx, y2 + flutuar), t2, Cores.TEXTO)
        texto(tela, "Trabalho de GAAL  ·  Geometria Analítica e Álgebra Linear",
              (cx, y3), 17, Cores.TEXTO_SUAVE, False, "center")

        # Os dois competidores enfeitando o título
        y_marcador = (y1 + y2) // 2
        desenhar_jogador(tela, (cx - dx, y_marcador + flutuar), Cores.JOGADOR_1, 1, 16, True, self.tempo)
        desenhar_jogador(tela, (cx + dx, y_marcador - flutuar), Cores.JOGADOR_2, 2, 16, True, self.tempo + 1)

        for botao in self.botoes:
            botao.desenhar(tela)
        dica = "Toque em Jogar para começar" if config.NO_NAVEGADOR else "Enter para jogar"
        texto(tela, dica, (cx, config.ALTURA - (16 if config.CELULAR else 28)), 14,
              Cores.TEXTO_SUAVE, False, "center")

    def _desenhar_regras(self, tela):
        escurecer_tela(tela, 120)
        if config.CELULAR:
            self._desenhar_regras_celular(tela)
            return
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

    def _desenhar_regras_celular(self, tela):
        rect = pygame.Rect(12, 10, config.LARGURA - 24, config.ALTURA - 82)
        painel(tela, rect)
        texto(tela, "COMO JOGAR", (rect.centerx, rect.top + 24), 26, Cores.DESTAQUE, True, "center")
        largura_coluna = (rect.width - 40) // 2
        for c, coluna in enumerate(REGRAS_CELULAR):
            x = rect.left + 24 + c * (largura_coluna + 16)
            y = rect.top + 52
            for titulo, cor, linhas in coluna:
                pygame.draw.rect(tela, cor, (x, y + 4, 5, 16), border_radius=3)
                texto(tela, titulo, (x + 12, y), 17, cor, True)
                y += 24
                for linha in linhas:
                    texto(tela, linha, (x + 12, y), 16, misturar(Cores.TEXTO, Cores.TEXTO_SUAVE, 0.2))
                    y += 21
                y += 8
        self.botao_voltar.desenhar(tela)
