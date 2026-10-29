"""
geometria.py — Base matemática do jogo (Geometria Analítica e Álgebra Linear).

Este módulo NÃO usa pygame: só vetores, ângulos, matrizes e distâncias.
Todas as partes do trabalho usam estas funções.

Resumo do que aparece aqui:
  * vetores no R², soma, multiplicação por escalar, norma, versor
  * produto escalar  u·v = |u||v|cos(θ)   -> ângulo entre vetores e projeções
  * determinante 2x2 det[u v]              -> orientação (esquerda/direita) e interseções
  * matriz de rotação R(θ)                 -> girar os obstáculos
  * coordenadas polares (r, θ)             -> setor circular
  * distância ponto-segmento por projeção ortogonal -> colisão
"""
import math

EPS = 1e-9


class Vetor:
    """Vetor (ou ponto) do R² com as operações da álgebra linear."""

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, outro):
        return Vetor(self.x + outro.x, self.y + outro.y)

    def __sub__(self, outro):
        return Vetor(self.x - outro.x, self.y - outro.y)

    def __mul__(self, k):
        return Vetor(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __truediv__(self, k):
        return Vetor(self.x / k, self.y / k)

    def __neg__(self):
        return Vetor(-self.x, -self.y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self):
        return f"Vetor({self.x:.2f}, {self.y:.2f})"

    def formatar(self, casas=2):
        """Texto do ponto no formato (x, y)."""
        return f"({self.x:.{casas}f}, {self.y:.{casas}f})"


# ------------------------------------------------------------ Operações ----

def produto_escalar(u, v):
    """u · v = u1*v1 + u2*v2"""
    return u.x * v.x + u.y * v.y


def determinante(u, v):
    """det [u v] = u1*v2 - u2*v1.
    Positivo: v está à ESQUERDA de u (sentido anti-horário).
    Negativo: v está à DIREITA de u.  Zero: u e v são paralelos."""
    return u.x * v.y - u.y * v.x


def norma(u):
    """|u| = sqrt(u1² + u2²)"""
    return math.hypot(u.x, u.y)


def distancia(p, q):
    """d(P, Q) = |Q - P|"""
    return norma(q - p)


def versor(u):
    """Vetor unitário na direção de u:  u / |u|"""
    n = norma(u)
    if n < EPS:
        return Vetor(0, 0)
    return u / n


def centroide(pontos):
    """Média dos vértices (baricentro do polígono)."""
    soma = Vetor(0, 0)
    for p in pontos:
        soma = soma + p
    return soma / len(pontos)


# ------------------------------------------------- Ângulos e coordenadas ----

def vetor_polar(r, theta):
    """Converte coordenadas polares (r, θ) em vetor: (r·cos θ, r·sin θ)."""
    return Vetor(r * math.cos(theta), r * math.sin(theta))


def angulo_do_vetor(u):
    """Ângulo θ (em radianos) que o vetor u faz com o eixo x positivo."""
    return math.atan2(u.y, u.x)


def angulo_entre(u, v):
    """Ângulo entre u e v usando o produto escalar:  cos θ = (u·v) / (|u||v|)."""
    nu, nv = norma(u), norma(v)
    if nu < EPS or nv < EPS:
        return 0.0
    cosseno = produto_escalar(u, v) / (nu * nv)
    return math.acos(max(-1.0, min(1.0, cosseno)))


def normalizar_angulo(a):
    """Leva qualquer ângulo para o intervalo [-π, π)."""
    return (a + math.pi) % (2 * math.pi) - math.pi


# ------------------------------------------------- Matriz de rotação ----

def matriz_rotacao(theta):
    """R(θ) = | cos θ  -sin θ |
              | sin θ   cos θ |"""
    c, s = math.cos(theta), math.sin(theta)
    return ((c, -s),
            (s, c))


def aplicar_matriz(m, v):
    """Produto matriz 2x2 por vetor:  M · v"""
    return Vetor(m[0][0] * v.x + m[0][1] * v.y,
                 m[1][0] * v.x + m[1][1] * v.y)


def rotacionar(v, theta):
    """Gira o vetor v de um ângulo θ em torno da origem: R(θ) · v"""
    return aplicar_matriz(matriz_rotacao(theta), v)


# ------------------------------------------ Retas, segmentos e polígonos ----

def orientacao(a, b, c):
    """det[(B - A) (C - A)]: diz se C está à esquerda (+) ou à direita (-) da reta AB."""
    return determinante(b - a, c - a)


def _esta_no_segmento(p, a, b):
    """Supondo P colinear com AB, verifica se P fica entre A e B."""
    return (min(a.x, b.x) - EPS <= p.x <= max(a.x, b.x) + EPS and
            min(a.y, b.y) - EPS <= p.y <= max(a.y, b.y) + EPS)


def segmentos_se_intersectam(p1, p2, q1, q2):
    """Os segmentos P1P2 e Q1Q2 se cruzam?
    Se cruzam quando P1 e P2 ficam em lados opostos da reta Q1Q2
    E Q1 e Q2 ficam em lados opostos da reta P1P2 (sinais dos determinantes)."""
    d1 = orientacao(q1, q2, p1)
    d2 = orientacao(q1, q2, p2)
    d3 = orientacao(p1, p2, q1)
    d4 = orientacao(p1, p2, q2)

    if ((d1 > EPS and d2 < -EPS) or (d1 < -EPS and d2 > EPS)) and \
       ((d3 > EPS and d4 < -EPS) or (d3 < -EPS and d4 > EPS)):
        return True

    # Casos em que algum ponto é colinear (encosta exatamente no outro segmento)
    if abs(d1) <= EPS and _esta_no_segmento(p1, q1, q2):
        return True
    if abs(d2) <= EPS and _esta_no_segmento(p2, q1, q2):
        return True
    if abs(d3) <= EPS and _esta_no_segmento(q1, p1, p2):
        return True
    if abs(d4) <= EPS and _esta_no_segmento(q2, p1, p2):
        return True
    return False


def ponto_no_poligono_convexo(p, vertices):
    """P está dentro de um polígono convexo (triângulo/quadrado)?
    Está dentro se fica do MESMO lado de todas as arestas, ou seja,
    se todos os determinantes orientacao(Vi, Vi+1, P) têm o mesmo sinal."""
    n = len(vertices)
    sinais = [orientacao(vertices[i], vertices[(i + 1) % n], p) for i in range(n)]
    return all(s >= -EPS for s in sinais) or all(s <= EPS for s in sinais)


def distancia_ponto_segmento(p, a, b):
    """Distância de P ao segmento AB usando projeção ortogonal:
    t = ((P - A)·(B - A)) / |B - A|²  (limitado a [0, 1]);
    o ponto mais próximo é A + t(B - A)."""
    ab = b - a
    comprimento2 = produto_escalar(ab, ab)
    if comprimento2 < EPS:
        return distancia(p, a)
    t = produto_escalar(p - a, ab) / comprimento2
    t = max(0.0, min(1.0, t))
    return distancia(p, a + ab * t)


def distancia_entre_segmentos(p1, p2, q1, q2):
    """Menor distância entre dois segmentos (0 se eles se cruzam)."""
    if segmentos_se_intersectam(p1, p2, q1, q2):
        return 0.0
    return min(distancia_ponto_segmento(p1, q1, q2),
               distancia_ponto_segmento(p2, q1, q2),
               distancia_ponto_segmento(q1, p1, p2),
               distancia_ponto_segmento(q2, p1, p2))
