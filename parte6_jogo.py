"""
PARTE 6 — Lógica do jogo para INICIAR e FINALIZAR

* Partida.iniciar(): gera a pista (parte 1), os obstáculos (partes 2 e 3),
  os jogadores e os turnos (parte 7) e sorteia o primeiro setor (parte 4).
* Durante a partida o jogo fica em um destes estados:
      MIRANDO  -> o jogador da vez escolhe o destino dentro do setor
      ANIMANDO -> o marcador anda (ou bate e volta) na tela
      FIM      -> alguém chegou: mostra o resultado e as estatísticas
* executar(): laço principal do pygame, alterna entre o menu (parte 8) e a partida.
"""
import math
import random

import pygame

import config
from geometria import distancia, normalizar_angulo
from obstaculo import desenhar_obstaculo
from parte1_plano import PlanoCartesiano, gerar_pontos_da_pista, desenhar_pista
from parte2_triangulos import gerar_triangulos
from parte3_quadrados import gerar_quadrados
from parte4_setor import gerar_setor, desenhar_setor
from parte5_movimento import validar_movimento, existe_jogada_valida, COLISAO, CHEGADA
from parte7_regras import criar_jogadores, ControleDeTurnos
from parte8_menu import Menu
from parte9_visual import (Cores, Botao, Particulas, Tremor, texto, texto_com_sombra, rotulo, painel,
                           desenhar_fundo, escurecer_tela, desenhar_jogador, desenhar_fantasma, desenhar_x,
                           desenhar_trajetoria, linha_tracejada, misturar, suavizar, suavizar_entrada)

MIRANDO, ANIMANDO, FIM = "mirando", "animando", "fim"


class Partida:
    def __init__(self, dificuldade):
        self.nome_dificuldade = dificuldade
        self.dificuldade = config.DIFICULDADES[dificuldade]
        self.plano = PlanoCartesiano(config.RECT_PLANO, config.PLANO_XMIN, config.PLANO_XMAX,
                                     config.PLANO_YMIN, config.PLANO_YMAX)
        self.particulas = Particulas()
        self.tremor = Tremor()
        cx, cy = config.LARGURA // 2, config.ALTURA // 2
        self.botoes_fim = [Botao((cx - 250, cy + 84, 240, 52), "Jogar novamente", "reiniciar", Cores.VALIDO),
                           Botao((cx + 10, cy + 84, 240, 52), "Menu principal", "menu", Cores.JOGADOR_1)]
        self.iniciar()

    # ================================================================ INICIAR ====
    def iniciar(self):
        self.rng = random.Random()
        self.tempo = 0.0
        self.pista = gerar_pontos_da_pista(self.rng)
        protegidos = self.pista.partidas + [self.pista.chegada]
        total = self.dificuldade["quadrados"] + self.dificuldade["triangulos"]
        self.obstaculos = []
        for _ in range(30):  # se não couberem todos, sorteia o tabuleiro de novo
            quadrados = gerar_quadrados(self.dificuldade["quadrados"], [], protegidos, self.rng)
            triangulos = gerar_triangulos(self.dificuldade["triangulos"], quadrados, protegidos, self.rng)
            if len(quadrados) + len(triangulos) > len(self.obstaculos):
                self.obstaculos = quadrados + triangulos
            if len(self.obstaculos) == total:
                break

        self.jogadores = criar_jogadores(self.pista.partidas)
        self.turnos = ControleDeTurnos(self.jogadores)
        self.mensagens = [("Partida iniciada! O Jogador 1 começa.", Cores.TEXTO)]
        self.marcas_batida = []   # [ponto, segundos restantes]
        self.mostrar_vertices = False
        self.animacao = None
        self.estado = MIRANDO
        self._preparar_jogada()

    def _preparar_jogada(self):
        self.setor = self._sortear_setor(self.turnos.jogador_atual)
        self.mira = self.setor.ponto(self.setor.raio * 0.6, self.setor.direcao)

    def _sortear_setor(self, jogador):
        """Sorteia setores até achar um que tenha pelo menos uma jogada sem batida."""
        setor = None
        for tentativa in range(60):
            desvio = None if tentativa < 20 else 180  # se estiver encurralado, libera qualquer direção
            setor = gerar_setor(jogador.posicao, self.pista.chegada, self.rng, self.dificuldade, desvio)
            if existe_jogada_valida(setor, self.plano, self.obstaculos):
                break
        return setor

    def _mensagem(self, novas):
        for nova in novas:
            if nova != self.mensagens[-1]:
                self.mensagens.append(nova)
        self.mensagens = self.mensagens[-2:]

    # ================================================================ EVENTOS ====
    def tratar_evento(self, evento):
        """Devolve 'menu', 'reiniciar' ou None."""
        if self.estado == FIM:
            for botao in self.botoes_fim:
                if botao.clicado(evento):
                    return botao.acao
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_r):
                    return "reiniciar"
                if evento.key in (pygame.K_ESCAPE, pygame.K_m):
                    return "menu"
            return None

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
            if evento.key == pygame.K_v:
                self.mostrar_vertices = not self.mostrar_vertices

        if self.estado != MIRANDO:
            return None

        if evento.type == pygame.MOUSEMOTION and self.plano.rect.collidepoint(evento.pos):
            self.mira = self.plano.para_plano(evento.pos)
        elif (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
              and self.plano.rect.collidepoint(evento.pos)):
            self.mira = self.plano.para_plano(evento.pos)
            self._confirmar_jogada()
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._confirmar_jogada()
            elif evento.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                self._ajustar_mira(evento.key, evento.mod & pygame.KMOD_SHIFT)
        return None

    def _ajustar_mira(self, tecla, rapido):
        """Setas mudam a mira em coordenadas polares: ←/→ giram θ, ↑/↓ mudam r."""
        r, theta = self.setor.polar_de(self.mira)
        passo_angulo = math.radians(5 if rapido else 1)
        passo_raio = 0.5 if rapido else 0.1
        if tecla == pygame.K_LEFT:
            theta += passo_angulo
        elif tecla == pygame.K_RIGHT:
            theta -= passo_angulo
        elif tecla == pygame.K_UP:
            r += passo_raio
        elif tecla == pygame.K_DOWN:
            r -= passo_raio
        r, theta = self.setor.limitar(r, theta)
        self.mira = self.setor.ponto(r, theta)

    def _confirmar_jogada(self):
        jogador = self.turnos.jogador_atual
        resultado = validar_movimento(jogador.posicao, self.mira, self.setor, self.plano,
                                      self.obstaculos, self.pista)
        if not resultado.valido:
            self._mensagem([(resultado.mensagem, Cores.INVALIDO)])
            self.tremor.iniciar(4, 0.2)
            return
        alvo = resultado.ponto_impacto if resultado.tipo == COLISAO else resultado.destino
        self.animacao = {
            "jogador": jogador, "resultado": resultado, "fase": "ida",
            "de": resultado.origem, "para": alvo, "t": 0.0,
            "duracao": min(0.9, 0.25 + 0.1 * distancia(resultado.origem, alvo)),
        }
        self.estado = ANIMANDO

    # ============================================================== ATUALIZAR ====
    def atualizar(self, dt):
        self.tempo += dt
        self.particulas.atualizar(dt)
        self.tremor.atualizar(dt)
        self.plano.deslocamento = self.tremor.deslocamento
        for marca in self.marcas_batida:
            marca[1] -= dt
        self.marcas_batida = [m for m in self.marcas_batida if m[1] > 0]

        if self.estado == ANIMANDO:
            self._animar(dt)
        elif self.estado == FIM:
            self.particulas.confete(config.LARGURA, [Cores.DESTAQUE, Cores.JOGADOR_1, Cores.JOGADOR_2,
                                                     Cores.VALIDO, Cores.TRIANGULO], 1)

    def _animar(self, dt):
        a = self.animacao
        res, jogador = a["resultado"], a["jogador"]
        a["t"] += dt / a["duracao"]
        curva = suavizar_entrada if (a["fase"] == "ida" and res.tipo == COLISAO) else suavizar
        jogador.pos_visual = a["de"] + (a["para"] - a["de"]) * curva(a["t"])
        if a["t"] < 1:
            return

        if a["fase"] == "ida" and res.tipo == COLISAO:
            # Bateu: faíscas, tremor e volta para a origem
            self.particulas.explodir(self.plano.para_tela(res.ponto_impacto),
                                     [Cores.INVALIDO, Cores.DESTAQUE, Cores.BRANCO], 35, 260, 0.7)
            self.tremor.iniciar(10, 0.4)
            self.marcas_batida.append([res.ponto_impacto, 4.0])
            a.update(fase="volta", de=res.ponto_impacto, para=res.origem, t=0.0, duracao=0.45)
            return

        jogador.pos_visual = res.destino
        if res.tipo == CHEGADA:
            self.particulas.explodir(self.plano.para_tela(self.pista.chegada),
                                     [Cores.DESTAQUE, jogador.cor, Cores.BRANCO], 60, 320, 1.2)
        self._encerrar_jogada(jogador, res)

    def _encerrar_jogada(self, jogador, resultado):
        self.animacao = None
        mensagens = self.turnos.aplicar_resultado(jogador, resultado)
        mensagens += self.turnos.avancar()
        self._mensagem(mensagens)
        if self.turnos.terminou:
            self.finalizar()
        else:
            self.estado = MIRANDO
            self._preparar_jogada()

    # ============================================================== FINALIZAR ====
    def finalizar(self):
        self.estado = FIM
        vencedores = self.turnos.vencedores
        if len(vencedores) == 1:
            self.titulo_fim = f"{vencedores[0].nome} venceu!"
            self.cor_fim = vencedores[0].cor
        else:
            self.titulo_fim = "Empate!"
            self.cor_fim = Cores.DESTAQUE
        self.subtitulo_fim = (f"Rodada {self.turnos.rodada}  ·  chegada em "
                              f"C{self.pista.chegada.formatar(1)}")
        centro = (config.LARGURA // 2, config.ALTURA // 2)
        self.particulas.explodir(centro, [self.cor_fim, Cores.DESTAQUE, Cores.BRANCO], 90, 420, 1.6)

    # ================================================================ DESENHO ====
    def desenhar(self, tela):
        desenhar_fundo(tela)
        self._desenhar_topo(tela)
        self.plano.desenhar(tela)
        atual = self.turnos.jogador_atual

        mouse = pygame.mouse.get_pos()
        mouse_plano = self.plano.para_plano(mouse) if self.plano.rect.collidepoint(mouse) else None

        tela.set_clip(self.plano.rect)
        desenhar_pista(tela, self.plano, self.pista, [j.cor for j in self.jogadores], self.tempo)
        for obst in self.obstaculos:
            destacado = mouse_plano is not None and obst.contem(mouse_plano)
            desenhar_obstaculo(tela, self.plano, obst, destacado, self.mostrar_vertices)
        for jogador in self.jogadores:
            desenhar_trajetoria(tela, [self.plano.para_tela(p) for p in jogador.trajetoria], jogador.cor)
        for ponto, _ in self.marcas_batida:
            desenhar_x(tela, self.plano.para_tela(ponto), Cores.INVALIDO, 7, 3)
        tela.set_clip(None)

        if self.estado == MIRANDO:
            desenhar_setor(tela, self.plano, self.setor, atual.cor, self.tempo)
            self._desenhar_mira(tela, atual)

        tela.set_clip(self.plano.rect)
        for jogador in sorted(self.jogadores, key=lambda j: j is atual):
            desenhar_jogador(tela, self.plano.para_tela(jogador.pos_visual), jogador.cor, jogador.numero,
                             11, jogador is atual and self.estado != FIM, self.tempo)
        tela.set_clip(None)

        self.particulas.desenhar(tela)
        self._desenhar_lateral(tela)
        self._desenhar_mensagens(tela)
        if self.estado == FIM:
            self._desenhar_fim(tela)

    def _desenhar_topo(self, tela):
        texto(tela, "Deslocamento com Obstáculos", (18, 14), 24, Cores.DESTAQUE, True)
        n_tri = sum(o.tipo == "triangulo" for o in self.obstaculos)
        n_quad = len(self.obstaculos) - n_tri
        plano_direita = config.RECT_PLANO[0] + config.RECT_PLANO[2]
        texto(tela, f"Dificuldade: {self.nome_dificuldade}   ·   {n_tri} triângulos   ·   "
                    f"{n_quad} quadrados   ·   Esc: menu", (plano_direita, 22), 15, Cores.TEXTO_SUAVE, False, "topright")
        lateral = pygame.Rect(config.RECT_LATERAL)
        texto(tela, f"Rodada {self.turnos.rodada}", (lateral.centerx, 32), 24, Cores.TEXTO, True, "center")

    def _desenhar_mira(self, tela, jogador):
        origem = self.plano.para_tela(jogador.posicao)
        alvo = self.plano.para_tela(self.mira)
        tela.set_clip(self.plano.rect)
        if self.setor.contem(self.mira) and self.plano.contem(self.mira, config.RAIO_JOGADOR):
            linha_tracejada(tela, Cores.BRANCO, origem, alvo, 2, 8, 5)
            desenhar_fantasma(tela, alvo, jogador.cor)
            rotulo(tela, f"Q{self.mira.formatar(2)}", (alvo[0], alvo[1] - 24), Cores.TEXTO, tamanho=12)
        else:
            linha_tracejada(tela, Cores.INVALIDO, origem, alvo, 1, 4, 6)
            desenhar_x(tela, alvo, Cores.INVALIDO)
            rotulo(tela, "fora do setor", (alvo[0], alvo[1] - 22), Cores.INVALIDO, tamanho=12)
        tela.set_clip(None)

    def _desenhar_lateral(self, tela):
        r = pygame.Rect(config.RECT_LATERAL)
        painel(tela, r)
        x, direita = r.left + 18, r.right - 18
        y = r.top + 14
        atual = self.turnos.jogador_atual

        def secao(titulo):
            nonlocal y
            texto(tela, titulo, (x, y), 13, Cores.TEXTO_SUAVE, True)
            pygame.draw.line(tela, Cores.PAINEL_BORDA, (x, y + 19), (direita, y + 19))
            y += 26

        def linha(rotulo_, valor, cor=Cores.TEXTO):
            nonlocal y
            texto(tela, rotulo_, (x, y), 15, Cores.TEXTO_SUAVE)
            texto(tela, valor, (direita, y), 15, cor, True, "topright")
            y += 21

        if self.estado == FIM:
            texto(tela, "FIM DE JOGO", (x, y), 13, Cores.TEXTO_SUAVE, True)
            texto(tela, self.titulo_fim, (x, y + 20), 22, self.cor_fim, True)
            y += 66
        else:
            texto(tela, "VEZ DE", (x, y), 13, Cores.TEXTO_SUAVE, True)
            y += 20
            desenhar_jogador(tela, (x + 12, y + 17), atual.cor, atual.numero, 12, True, self.tempo)
            texto(tela, atual.nome, (x + 34, y), 26, atual.cor, True)
            y += 46

            s = self.setor
            phi = math.degrees(normalizar_angulo(s.direcao))
            alfa = math.degrees(s.abertura)
            secao("SETOR CIRCULAR")
            linha("Centro P", s.centro.formatar(2))
            linha("Raio", f"R = {s.raio:.2f}")
            linha("Abertura", f"α = {alfa:.0f}°")
            linha("Direção", f"φ = {phi:.0f}°")
            linha("Ângulos válidos", f"{phi - alfa / 2:.0f}° a {phi + alfa / 2:.0f}°")
            y += 6

            r_mira, theta = s.polar_de(self.mira)
            secao("MIRA")
            linha("Destino Q", self.mira.formatar(2))
            linha("Distância r", f"{r_mira:.2f}")
            linha("Ângulo θ", f"{phi + math.degrees(theta - s.direcao):.0f}°")
            dentro = s.contem(self.mira) and self.plano.contem(self.mira, config.RAIO_JOGADOR)
            texto(tela, "Dentro do setor" if dentro else "Fora do setor", (x, y + 1), 15,
                  Cores.VALIDO if dentro else Cores.INVALIDO, True)
            y += 30

        secao("JOGADORES")
        for jogador in self.jogadores:
            card = pygame.Rect(x - 6, y, r.width - 24, 62)
            pygame.draw.rect(tela, misturar(Cores.PAINEL, jogador.cor, 0.12), card, border_radius=10)
            if jogador is atual and self.estado != FIM:
                pygame.draw.rect(tela, jogador.cor, card, 2, border_radius=10)
            pygame.draw.circle(tela, jogador.cor, (card.left + 14, card.top + 15), 6)
            texto(tela, jogador.nome, (card.left + 26, card.top + 4), 16, jogador.cor, True)
            if jogador.chegou:
                status, cor = "Chegou!", Cores.DESTAQUE
            elif jogador.turnos_bloqueados:
                status, cor = "Perde a vez", Cores.INVALIDO
            else:
                status, cor = "", Cores.TEXTO
            texto(tela, status, (card.right - 10, card.top + 6), 13, cor, True, "topright")
            dist = distancia(jogador.posicao, self.pista.chegada)
            texto(tela, f"Posição {jogador.posicao.formatar(1)}   Falta {dist:.1f}",
                  (card.left + 12, card.top + 25), 13, Cores.TEXTO)
            texto(tela, f"Jogadas {jogador.jogadas}   ·   Batidas {jogador.batidas}",
                  (card.left + 12, card.top + 42), 13, Cores.TEXTO_SUAVE)
            y += 68

        texto(tela, "Mouse: mirar · Clique: jogar · V: vértices", (r.centerx, r.bottom - 42), 13,
              Cores.TEXTO_SUAVE, False, "center")
        texto(tela, "Setas: ajuste fino · Enter: confirmar", (r.centerx, r.bottom - 22), 13,
              Cores.TEXTO_SUAVE, False, "center")

    def _desenhar_mensagens(self, tela):
        r = pygame.Rect(config.RECT_MENSAGEM)
        painel(tela, r, raio=12)
        for i, (mensagem, cor) in enumerate(reversed(self.mensagens)):
            if i == 0:
                texto(tela, mensagem, (r.left + 16, r.top + 7), 16, cor, True)
            else:
                texto(tela, mensagem, (r.left + 16, r.top + 32), 14, misturar(cor, Cores.PAINEL, 0.4))

    def _desenhar_fim(self, tela):
        escurecer_tela(tela, 150)
        caixa = pygame.Rect(0, 0, 600, 350)
        caixa.center = (config.LARGURA // 2, config.ALTURA // 2)
        painel(tela, caixa, borda=self.cor_fim)
        texto_com_sombra(tela, self.titulo_fim, (caixa.centerx, caixa.top + 48), 42, self.cor_fim)
        texto(tela, self.subtitulo_fim, (caixa.centerx, caixa.top + 92), 16, Cores.TEXTO_SUAVE, False, "center")

        colunas = [caixa.left + 50, caixa.left + 360, caixa.left + 490]
        y = caixa.top + 122
        for jogador, cx in zip(self.jogadores, colunas[1:]):
            texto(tela, jogador.nome, (cx, y), 16, jogador.cor, True, "midtop")
        y += 28
        linhas = [("Jogadas", lambda j: str(j.jogadas)),
                  ("Batidas", lambda j: str(j.batidas)),
                  ("Distância percorrida", lambda j: f"{j.distancia_percorrida:.2f}")]
        for nome, valor in linhas:
            pygame.draw.line(tela, Cores.PAINEL_BORDA, (colunas[0], y - 4), (caixa.right - 50, y - 4))
            texto(tela, nome, (colunas[0], y), 16, Cores.TEXTO)
            for jogador, cx in zip(self.jogadores, colunas[1:]):
                texto(tela, valor(jogador), (cx, y), 16, Cores.TEXTO, True, "midtop")
            y += 26

        for botao in self.botoes_fim:
            botao.desenhar(tela)
        texto(tela, "R: jogar novamente  ·  Esc: menu", (caixa.centerx, caixa.bottom - 18), 13,
              Cores.TEXTO_SUAVE, False, "center")


# ======================================================== LAÇO PRINCIPAL ====
def executar():
    pygame.init()
    pygame.display.set_caption(config.TITULO)
    tela = pygame.display.set_mode((config.LARGURA, config.ALTURA), pygame.SCALED | pygame.RESIZABLE)
    pygame.key.set_repeat(250, 35)
    relogio = pygame.time.Clock()

    dificuldade = config.DIFICULDADE_PADRAO
    cena = Menu(dificuldade)
    while True:
        dt = min(relogio.tick(config.FPS) / 1000, 0.05)
        for evento in pygame.event.get():
            acao = "sair" if evento.type == pygame.QUIT else cena.tratar_evento(evento)
            if acao == "sair":
                pygame.quit()
                return
            if acao == "jogar":
                dificuldade = cena.dificuldade
                cena = Partida(dificuldade)
            elif acao == "reiniciar":
                cena = Partida(dificuldade)
            elif acao == "menu":
                cena = Menu(dificuldade)
        cena.atualizar(dt)
        cena.desenhar(tela)
        pygame.display.flip()
