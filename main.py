"""
Deslocamento com Obstáculos — Trabalho de GAAL

Para jogar:   python main.py
Versão web:   python -m pygbag --build .   (gera build/web para publicar)
"""
import asyncio

import pygame  # precisa estar aqui para o pygbag carregar o pygame no navegador

from parte6_jogo import executar

if __name__ == "__main__":
    asyncio.run(executar())
