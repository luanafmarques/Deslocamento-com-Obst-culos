"""
PARTE 9 — Embelezar a interface do jogo

Tudo o que é "aparência" e é usado por várias partes fica aqui:
  * paleta de cores e fontes
  * fundo em degradê, painéis arredondados, rótulos, linhas tracejadas
  * marcador dos jogadores com brilho pulsante
  * bandeira quadriculada da chegada
  * botões com animação de hover (usados no menu e na tela final)
  * partículas (batida, chegada, confete) e tremor de tela
"""
import math
import random

import pygame


class Cores:
    FUNDO_TOPO = (12, 16, 30)
    FUNDO_BASE = (28, 36, 64)
    PLANO = (16, 22, 40)
    GRADE_FINA = (28, 37, 62)
    GRADE_GROSSA = (42, 55, 90)
    EIXOS = (160, 176, 214)
    TEXTO = (232, 238, 250)
    TEXTO_SUAVE = (140, 152, 186)
    PAINEL = (24, 31, 54)
    PAINEL_BORDA = (58, 74, 118)
    DESTAQUE = (255, 206, 84)
    VALIDO = (94, 224, 146)
    INVALIDO = (242, 84, 92)
    TRIANGULO = (236, 96, 128)
    QUADRADO = (150, 112, 244)
    JOGADOR_1 = (72, 180, 255)
    JOGADOR_2 = (255, 146, 64)
    BRANCO = (255, 255, 255)
    PRETO = (8, 10, 18)


def misturar(c1, c2, t):
    """Interpolação linear entre duas cores: c1 + t(c2 - c1)."""
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def suavizar(t):
    """Curva 'ease-out' para animações (começa rápido, termina devagar)."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def suavizar_entrada(t):
    """Curva 'ease-in' (começa devagar, termina rápido)."""
    t = max(0.0, min(1.0, t))
    return t ** 2


# ---------------------------------------------------------------- Texto ----

_fontes = {}


def fonte(tamanho, negrito=False):
    chave = (tamanho, negrito)
    if chave not in _fontes:
        _fontes[chave] = pygame.font.SysFont("segoeui,arial,dejavusans", tamanho, bold=negrito)
    return _fontes[chave]


def texto(superficie, conteudo, pos, tamanho=16, cor=Cores.TEXTO, negrito=False, ancora="topleft"):
    """Escreve um texto e devolve o retângulo ocupado."""
    img = fonte(tamanho, negrito).render(str(conteudo), True, cor)
    rect = img.get_rect(**{ancora: (round(pos[0]), round(pos[1]))})
    superficie.blit(img, rect)
    return rect


def texto_com_sombra(superficie, conteudo, pos, tamanho, cor, ancora="center", deslocamento=3):
    texto(superficie, conteudo, (pos[0] + deslocamento, pos[1] + deslocamento), tamanho, Cores.PRETO, True, ancora)
    return texto(superficie, conteudo, pos, tamanho, cor, True, ancora)


def rotulo(superficie, conteudo, centro, cor_texto=Cores.TEXTO, cor_fundo=(10, 14, 26), tamanho=14, alpha=215):
    """Texto dentro de uma 'pílula' escura (fica legível em cima de qualquer coisa)."""
    img = fonte(tamanho, True).render(conteudo, True, cor_texto)
    caixa = img.get_rect(center=(round(centro[0]), round(centro[1]))).inflate(14, 4)
    camada = pygame.Surface(caixa.size, pygame.SRCALPHA)
    pygame.draw.rect(camada, (*cor_fundo, alpha), camada.get_rect(), border_radius=caixa.height // 2)
    superficie.blit(camada, caixa.topleft)
    superficie.blit(img, img.get_rect(center=caixa.center))
    return caixa


# ---------------------------------------------------- Fundo e painéis ----

_fundos = {}


def desenhar_fundo(superficie):
    """Degradê vertical (calculado uma vez só e reaproveitado)."""
    tamanho = superficie.get_size()
    if tamanho not in _fundos:
        largura, altura = tamanho
        fundo = pygame.Surface(tamanho)
        for y in range(altura):
            pygame.draw.line(fundo, misturar(Cores.FUNDO_TOPO, Cores.FUNDO_BASE, y / altura), (0, y), (largura, y))
        _fundos[tamanho] = fundo
    superficie.blit(_fundos[tamanho], (0, 0))


def painel(superficie, rect, cor=Cores.PAINEL, borda=Cores.PAINEL_BORDA, raio=14, alpha=235):
    rect = pygame.Rect(rect)
    camada = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(camada, (*cor, alpha), camada.get_rect(), border_radius=raio)
    if borda:
        pygame.draw.rect(camada, (*borda, 255), camada.get_rect(), width=2, border_radius=raio)
    superficie.blit(camada, rect.topleft)


def escurecer_tela(superficie, alpha=170):
    camada = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    camada.fill((5, 8, 16, alpha))
    superficie.blit(camada, (0, 0))


# ------------------------------------------------------------ Desenhos ----

def linha_tracejada(superficie, cor, p1, p2, largura=2, traco=9, espaco=6):
    x1, y1 = p1
    x2, y2 = p2
    comprimento = math.hypot(x2 - x1, y2 - y1)
    if comprimento < 1:
        return
    ux, uy = (x2 - x1) / comprimento, (y2 - y1) / comprimento
    d = 0.0
    while d < comprimento:
        fim = min(d + traco, comprimento)
        pygame.draw.line(superficie, cor, (x1 + ux * d, y1 + uy * d), (x1 + ux * fim, y1 + uy * fim), largura)
        d += traco + espaco


def brilho(superficie, centro, raio, cor, intensidade=90):
    """Halo suave: vários círculos translúcidos empilhados."""
    r = max(2, int(raio))
    camada = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    camadas = 6
    for k in range(camadas, 0, -1):
        pygame.draw.circle(camada, (*cor, intensidade // camadas), (r, r), max(1, r * k // camadas))
    superficie.blit(camada, (round(centro[0]) - r, round(centro[1]) - r))


def desenhar_jogador(superficie, centro, cor, numero, raio=11, destaque=False, tempo=0.0):
    """Marcador redondo do jogador; o jogador da vez ganha um brilho pulsante."""
    cx, cy = round(centro[0]), round(centro[1])
    if destaque:
        pulso = 1 + 0.18 * math.sin(tempo * 5)
        brilho(superficie, (cx, cy), raio * 2.8 * pulso, cor, 130)
    pygame.draw.circle(superficie, misturar(cor, Cores.PRETO, 0.6), (cx, cy + 3), raio)
    pygame.draw.circle(superficie, cor, (cx, cy), raio)
    pygame.draw.circle(superficie, Cores.BRANCO, (cx, cy), raio, 2)
    texto(superficie, numero, (cx, cy), 13, Cores.PRETO, True, "center")


def desenhar_fantasma(superficie, centro, cor, raio=11, alpha=110):
    """Marcador translúcido (prévia do destino)."""
    camada = pygame.Surface((raio * 2 + 4, raio * 2 + 4), pygame.SRCALPHA)
    meio = (raio + 2, raio + 2)
    pygame.draw.circle(camada, (*cor, alpha), meio, raio)
    pygame.draw.circle(camada, (255, 255, 255, alpha + 60), meio, raio, 2)
    superficie.blit(camada, (round(centro[0]) - raio - 2, round(centro[1]) - raio - 2))


def desenhar_x(superficie, centro, cor, tamanho=8, largura=3):
    cx, cy = centro
    pygame.draw.line(superficie, cor, (cx - tamanho, cy - tamanho), (cx + tamanho, cy + tamanho), largura)
    pygame.draw.line(superficie, cor, (cx - tamanho, cy + tamanho), (cx + tamanho, cy - tamanho), largura)


def desenhar_trajetoria(superficie, pontos_tela, cor):
    """Caminho já percorrido: segmentos translúcidos com um ponto em cada parada."""
    if len(pontos_tela) < 2:
        return
    camada = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(camada, (*cor, 120), False, pontos_tela, 3)
    for p in pontos_tela:
        pygame.draw.circle(camada, (*cor, 190), (round(p[0]), round(p[1])), 4)
    superficie.blit(camada, (0, 0))


_bandeiras = {}


def bandeira_quadriculada(superficie, centro, raio):
    """Círculo com xadrez preto e branco (ponto de chegada)."""
    r = max(4, int(raio))
    if r not in _bandeiras:
        d = r * 2
        img = pygame.Surface((d, d), pygame.SRCALPHA)
        celula = max(3, d // 6)
        for i in range(0, d, celula):
            for j in range(0, d, celula):
                cor = (245, 245, 245, 255) if (i // celula + j // celula) % 2 == 0 else (20, 20, 24, 255)
                pygame.draw.rect(img, cor, (i, j, celula, celula))
        mascara = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(mascara, (255, 255, 255, 255), (r, r), r)
        img.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _bandeiras[r] = img
    superficie.blit(_bandeiras[r], (round(centro[0]) - r, round(centro[1]) - r))


# --------------------------------------------------------------- Botão ----

class Botao:
    def __init__(self, rect, rotulo, acao, cor=Cores.JOGADOR_1, tamanho=22):
        self.rect = pygame.Rect(rect)
        self.rotulo = rotulo
        self.acao = acao
        self.cor = cor
        self.tamanho = tamanho
        self._hover = 0.0

    def clicado(self, evento):
        return (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                and self.rect.collidepoint(evento.pos))

    def desenhar(self, superficie):
        em_cima = self.rect.collidepoint(pygame.mouse.get_pos())
        self._hover += ((1.0 if em_cima else 0.0) - self._hover) * 0.25
        h = self._hover
        r = self.rect.inflate(round(h * 10), round(h * 4))
        if h > 0.05:
            brilho(superficie, r.center, r.width * 0.55, self.cor, int(50 * h))
        pygame.draw.rect(superficie, misturar(Cores.PAINEL, self.cor, 0.18 + 0.32 * h), r, border_radius=12)
        pygame.draw.rect(superficie, misturar(self.cor, Cores.BRANCO, 0.3 * h), r, 2, border_radius=12)
        texto(superficie, self.rotulo, r.center, self.tamanho, Cores.TEXTO, True, "center")


# ---------------------------------------------------- Efeitos especiais ----

class Particula:
    __slots__ = ("x", "y", "vx", "vy", "vida", "vida_total", "cor", "tamanho", "gravidade")

    def __init__(self, x, y, vx, vy, vida, cor, tamanho, gravidade):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.vida = self.vida_total = vida
        self.cor, self.tamanho, self.gravidade = cor, tamanho, gravidade


class Particulas:
    def __init__(self):
        self.lista = []

    def explodir(self, centro, cores, quantidade=30, velocidade=220, vida=0.9, gravidade=0.0):
        for _ in range(quantidade):
            angulo = random.uniform(0, 2 * math.pi)
            v = random.uniform(0.3, 1.0) * velocidade
            self.lista.append(Particula(centro[0], centro[1], math.cos(angulo) * v, math.sin(angulo) * v,
                                        vida * random.uniform(0.6, 1.0), random.choice(cores),
                                        random.uniform(2, 5), gravidade))

    def confete(self, largura, cores, quantidade=6):
        for _ in range(quantidade):
            self.lista.append(Particula(random.uniform(0, largura), -10, random.uniform(-40, 40),
                                        random.uniform(80, 200), random.uniform(3, 5),
                                        random.choice(cores), random.uniform(3, 6), 30))

    def atualizar(self, dt):
        for p in self.lista:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravidade * dt
            p.vx *= 1 - 1.5 * dt
            if p.gravidade == 0:
                p.vy *= 1 - 1.5 * dt
            p.vida -= dt
        self.lista = [p for p in self.lista if p.vida > 0]

    def desenhar(self, superficie):
        for p in self.lista:
            fracao = p.vida / p.vida_total
            pygame.draw.circle(superficie, p.cor, (round(p.x), round(p.y)), max(1, round(p.tamanho * fracao + 0.5)))


class Tremor:
    """Faz a tela tremer por alguns instantes (usado quando alguém bate)."""

    def __init__(self):
        self.intensidade = 0.0
        self.duracao = 1.0
        self.restante = 0.0
        self.deslocamento = (0, 0)

    def iniciar(self, intensidade=9, duracao=0.35):
        self.intensidade, self.duracao, self.restante = intensidade, duracao, duracao

    def atualizar(self, dt):
        self.restante = max(0.0, self.restante - dt)
        k = self.intensidade * self.restante / self.duracao
        self.deslocamento = (random.uniform(-k, k), random.uniform(-k, k)) if k > 0 else (0, 0)
