import pygame
import math

# chamando o pygame e os efeitos sonoros
pygame.init()
pygame.mixer.init()

# layout da tela
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

# cores
preto = (10, 10, 20)
branco = (255, 255, 255)
amarelo = (255, 234, 0)
azul = (50, 150, 255)
verde = (0, 255, 100)
vermelho = (255, 50, 50)
cinza = (100, 100, 100)
cinza_claro  = (255, 255, 235)
preto_nave = (15, 15, 20)
laranja = (255, 165, 0)
roxo = (200, 50, 255)
rosa = (255, 100, 180)

# fontes
fonte_gigante = pygame.font.SysFont("Arial", 45, bold=True)
fonte_media = pygame.font.SysFont("Arial", 32, bold=True) 
fonte_pequena = pygame.font.SysFont("Arial", 24, bold=True)
fonte_controles = pygame.font.SysFont("Arial", 18, bold=True)

# efeitos sonoros
def gerar_som(tipo):
    """Gera um som de acerto (agudo) ou erro (grave)"""
    frequencia = 880 if tipo == "acerto" else 220
    duracao = 0.1 if tipo == "acerto" else 0.3
    amostragem = 44100
    num_amostras = int(duracao * amostragem) # Corrected: init changed to int

    buffer = bytearray()
    for i in range(num_amostras):
        t = i / amostragem
        # onda quadrada básica
        valor = 127 if math.sin(2 * math.pi * frequencia * t) > 0 else -128
        buffer.append(valor & 0xFF)

    som = pygame.mixer.Sound(buffer=bytes(buffer))
    som.set_volume(0.2)
    return som

som_acerto = gerar_som("acerto")
som_erro = gerar_som("erro")

# sistema de fases
# cada fase tem uma palavra, um intervalo de spawn
# quanto menor for o intervalo, mais rápido
# uma velocidade das letras e a chance dessa aparecer
fases = ["AZUL", "MARTE", "COMETA", "FOGUETE", "GALAXIA"]
intervalos_spawn = [45, 40, 36, 32, 28]
multiplicadores_velocidade = [1.0, 1.15, 1.3, 1.45, 1.6]
chances_letra_certa = [0.45, 0.40, 0.35, 0.32, 0.28]

# estados possíveis
ESTADO_PAUSADO = "pausado"
ESTADO_JOGANDO = "jogando"
ESTADO_VITORIA = "vitoria_final"