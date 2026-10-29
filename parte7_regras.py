"""
PARTE 7 — Regras do jogo e os dois jogadores

Regras:
  * Os jogadores se alternam: Jogador 1, Jogador 2, Jogador 1, ...
    Cada par de vezes forma uma RODADA.
  * Batida (o segmento do movimento toca um obstáculo):
      - o jogador volta para onde estava (não anda nada)
      - e perde a próxima vez (PUNICAO_TURNOS em config.py)
  * Quem tocar o círculo de chegada termina a corrida, mas a rodada vai até o
    fim: se o Jogador 1 chega, o Jogador 2 ainda tem a vez dele na mesma rodada.
    Se os dois chegarem na mesma rodada, é EMPATE.
"""
import config
from geometria import distancia
from parte5_movimento import COLISAO, CHEGADA
from parte9_visual import Cores


class Jogador:
    def __init__(self, numero, nome, cor, partida):
        self.numero = numero
        self.nome = nome
        self.cor = cor
        self.partida = partida
        self.posicao = partida        # posição "oficial" (usada nas regras)
        self.pos_visual = partida     # posição desenhada (muda durante a animação)
        self.trajetoria = [partida]   # pontos por onde passou
        self.jogadas = 0
        self.batidas = 0
        self.turnos_bloqueados = 0
        self.chegou = False

    @property
    def distancia_percorrida(self):
        return sum(distancia(a, b) for a, b in zip(self.trajetoria, self.trajetoria[1:]))


def criar_jogadores(partidas):
    """O segundo jogador é uma réplica do primeiro, só muda nome, cor e ponto de partida."""
    return [Jogador(1, "Jogador 1", Cores.JOGADOR_1, partidas[0]),
            Jogador(2, "Jogador 2", Cores.JOGADOR_2, partidas[1])]


class ControleDeTurnos:
    def __init__(self, jogadores):
        self.jogadores = jogadores
        self.indice = 0
        self.rodada = 1
        self.terminou = False
        self.vencedores = []

    @property
    def jogador_atual(self):
        return self.jogadores[self.indice]

    def aplicar_resultado(self, jogador, resultado):
        """Aplica uma jogada já validada (parte 5). Devolve mensagens (texto, cor)."""
        jogador.jogadas += 1

        if resultado.tipo == COLISAO:
            jogador.batidas += 1
            jogador.turnos_bloqueados += config.PUNICAO_TURNOS
            return [(f"{jogador.nome} bateu no {resultado.obstaculo.nome} em "
                     f"{resultado.ponto_impacto.formatar(1)}! Volta e perde a próxima vez.", Cores.INVALIDO)]

        jogador.posicao = resultado.destino
        jogador.trajetoria.append(resultado.destino)
        if resultado.tipo == CHEGADA:
            jogador.chegou = True
            return [(f"{jogador.nome} alcançou a chegada na rodada {self.rodada}!", Cores.DESTAQUE)]
        return [(f"{jogador.nome} andou de {resultado.origem.formatar(2)} até "
                 f"{resultado.destino.formatar(2)}.", jogador.cor)]

    def avancar(self):
        """Passa a vez para o próximo jogador que pode jogar. Devolve mensagens."""
        mensagens = []
        while True:
            self.indice += 1
            if self.indice >= len(self.jogadores):
                # Fim da rodada: alguém chegou?
                chegaram = [j for j in self.jogadores if j.chegou]
                if chegaram:
                    self.terminou = True
                    self.vencedores = chegaram
                    self.indice = len(self.jogadores) - 1
                    return mensagens
                self.indice = 0
                self.rodada += 1

            jogador = self.jogador_atual
            if jogador.turnos_bloqueados > 0:
                jogador.turnos_bloqueados -= 1
                mensagens.append((f"{jogador.nome} perdeu a vez (punição pela batida).", Cores.TEXTO_SUAVE))
                continue
            return mensagens
