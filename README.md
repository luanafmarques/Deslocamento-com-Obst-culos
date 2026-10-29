# Deslocamento com Obstáculos — Trabalho de GAAL

Jogo para 2 competidores em um **plano cartesiano**. Cada um sai do seu ponto de
partida e tenta chegar primeiro ao **mesmo ponto de chegada**, desviando de
obstáculos **triangulares (3 pontos)** e **quadrados (4 pontos)**. A cada jogada é
sorteado um **setor circular** (raio R e ângulo α) de movimentos possíveis; o jogador
escolhe um destino dentro dele, a jogada é validada e a nova posição é exibida.

## Como rodar

1. Instale o Python 3 (em python.org, marque **"Add Python to PATH"**).
2. Instale o pygame:
   ```
   pip install -r requirements.txt
   ```
3. Rode o jogo:
   ```
   python main.py
   ```
   No Windows também dá para dar dois cliques em `jogar.bat`.

## Regras

- Os jogadores se alternam (Jogador 1, Jogador 2, ...). Cada par de vezes é uma **rodada**.
- Na sua vez aparece o setor circular: centro na sua posição, raio **R**, abertura **α**,
  apontando mais ou menos para a chegada.
- Escolha um destino **dentro do setor** (mouse ou setas) e confirme.
  O movimento é o **segmento de reta** entre a posição atual e o destino.
- Destino fora do setor ou fora do plano: jogada inválida, escolha de novo.
- **Batida**: se o segmento encostar em um obstáculo, o jogador volta para onde
  estava e **perde a próxima vez**.
- Quem tocar o círculo de chegada vence. A rodada sempre termina: se os dois
  chegarem na mesma rodada, é **empate**.

Controles: mouse mira, clique joga · setas = ajuste fino (Shift = rápido) ·
Enter/Espaço confirma · V mostra as coordenadas dos vértices · Esc volta ao menu.

## Divisão do trabalho (9 partes)

| # | Tarefa | Arquivo |
|---|--------|---------|
| 1 | Plano cartesiano, pontos de partida e chegada, linha de largada | `parte1_plano.py` |
| 2 | Gerador de obstáculos triângulo (com distância mínima) | `parte2_triangulos.py` |
| 3 | Gerador de obstáculos quadrado (com distância mínima) | `parte3_quadrados.py` |
| 4 | Ponto inicial da jogada e setor circular com raio e ângulo visuais | `parte4_setor.py` |
| 5 | Executar e validar o movimento (colisão com obstáculos, chegada) | `parte5_movimento.py` |
| 6 | Lógica para iniciar / finalizar o jogo (estados, laço principal) | `parte6_jogo.py` |
| 7 | Regras (turnos, punição por batida) e criação do segundo jogador | `parte7_regras.py` |
| 8 | Interface gráfica do menu inicial | `parte8_menu.py` |
| 9 | Embelezar a interface (cores, brilho, animações, partículas) | `parte9_visual.py` |

Arquivos de apoio (usados por várias partes):

- `geometria.py`: toda a matemática (vetores, produto escalar, determinante, rotação...).
- `obstaculo.py`: base comum das partes 2 e 3 (classe do obstáculo e regra de espaçamento).
- `config.py`: constantes (tamanho do plano, distâncias mínimas, dificuldades).
- `main.py`: ponto de entrada.

## A matemática de cada parte

**Parte 1 — Plano cartesiano.** Conversão plano ↔ tela por uma transformação afim:
`px = esq + (x - xmin)·escala`, `py = base - (y - ymin)·escala` (o y é invertido porque
na tela ele cresce para baixo). A chegada C é sorteada e as partidas A e B ficam
simétricas em relação à reta horizontal por C, então `d(A, C) = d(B, C)`: a corrida é justa.

**Partes 2 e 3 — Obstáculos.** Cada forma é um "molde" pré-definido em torno da origem.
Ela é levada ao lugar sorteado por **rotação + translação**:
`V_final = centro + R(θ)·V_molde`, com `R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]`.
A rotação preserva distâncias e ângulos, então o quadrado continua quadrado.
Espaçamento: cada obstáculo cabe no seu círculo circunscrito (centro = baricentro).
Exigimos `d(C1, C2) ≥ r1 + r2 + folga` entre obstáculos e uma folga até as partidas,
a chegada e as bordas. Como a folga é maior que o diâmetro do marcador, **sempre existe
passagem**: a pista nunca fica 100% bloqueada.

**Parte 4 — Setor circular.** Centro P (posição do jogador), raio R, direção φ e abertura α.
Um ponto Q está no setor se, com `v = Q - P` e `u = (cos φ, sin φ)`:
`|v| ≤ R` e `ângulo(v, u) ≤ α/2`, onde `cos(ângulo) = (v·u) / (|v||u|)` (**produto escalar**).
A mira usa **coordenadas polares**: `Q = P + (r cos θ, r sin θ)`.

**Parte 5 — Movimento e colisão.** O movimento é o segmento `P(t) = O + t(D - O)`, `0 ≤ t ≤ 1`.
- Ponto dentro do triângulo/quadrado: o ponto fica do mesmo lado de todas as arestas,
  ou seja, os **determinantes** `det[(B - A) (P - A)]` têm o mesmo sinal.
- Dois segmentos se cruzam quando os determinantes mudam de sinal (cada segmento separa
  as pontas do outro).
- Distância ponto-segmento por **projeção ortogonal**:
  `t = ((P - A)·(B - A)) / |B - A|²`; o ponto mais próximo é `A + t(B - A)`.
- Bateu se a distância do segmento ao obstáculo for menor que o raio do marcador.
- Chegada: resolve `|O + t·d - C|² = r²`, uma **equação do 2º grau** em t.

**Parte 7 — Regras.** O Jogador 2 é a mesma classe do Jogador 1 com outra cor e outro
ponto de partida. O controle de turnos pula quem está punido e só encerra o jogo no
fim da rodada.

## Ajustes

Em `config.py` dá para mudar tudo sem mexer no resto: quantidade de obstáculos por
dificuldade, faixa do raio e do ângulo do setor, folga entre obstáculos, punição etc.
