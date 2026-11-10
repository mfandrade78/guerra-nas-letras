import pygame
import math
import sqlite3
from banco_dados import registrar_vitoria
from configuracoes import (
    largura, altura, preto, branco, amarelo, verde, fonte_gigante, fonte_media, fonte_pequena, fonte_controles, som_acerto, som_erro, fases, intervalos_spawn, multiplicadores_velocidade, chances_letra_certa, ESTADO_PAUSADO, ESTADO_JOGANDO, ESTADO_VITORIA
)
from entidades import Nave, Projetil, LetraFlutuante

# janela e relógio
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Guerra nas Letras")
relogio = pygame.time.Clock()

# variáveis globais de progresso (iniciar_fase)
fase_atual = 0
frase_alvo = ""
letras_restantes = []
letras_acertadas = []
intervalo_spawn = 45
multiplicador_velocidade = 1.0
chance_letra_certa = 0.4
fase_recem_concluida = None # guarda o índice da fase que acabou de ser concluída, para exibir
# a mensagem de "FASE X CONCLUÍDA!" durante a pausa
projeteis = []
letras = []
tempo_spawn = 0
estado_jogo = ESTADO_PAUSADO # o jogo começa pausado, esperando ENTER
tempo_inicio_partida = None
duracao_partida = None
log_final = ""
erro_banco = None
contagem_teclas = {
    pygame.K_LEFT: 0,
    pygame.K_RIGHT: 0,
    pygame.K_SPACE: 0,
}


def formatar_duracao(segundos):
    horas, resto = divmod(int(segundos), 3600)
    minutos, segundos = divmod(resto, 60)
    return f"{horas:02}:{minutos:02}:{segundos:02}"


def iniciar_fase(indice):
    """Configura todas as variáveis globais para a fase indicada"""
    global fase_atual, frase_alvo, letras_restantes, letras_acertadas
    global intervalo_spawn, multiplicador_velocidade, chance_letra_certa
    global tempo_spawn, letras, projeteis
    
    fase_atual = indice
    frase_alvo = fases[indice]
    letras_restantes = [c for c in frase_alvo if c != " "]
    letras_acertadas = []
    intervalo_spawn = intervalos_spawn[indice]
    multiplicador_velocidade = multiplicadores_velocidade[indice]
    chance_letra_certa = chances_letra_certa[indice]
    tempo_spawn = 0
    letras = []
    projeteis = []

# inicializa a primeira fase
nave = Nave()
iniciar_fase(0)

# loop principal do jogo
jogando = True
while jogando:
    tela.fill(preto)
    teclas = pygame.key.get_pressed()

    # eventos
    for evento in pygame.event.get(): 
        if evento.type == pygame.QUIT: 
            jogando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key in contagem_teclas:
                contagem_teclas[evento.key] += 1
            if evento.key == pygame.K_SPACE and estado_jogo  == ESTADO_JOGANDO and len(letras_restantes) > 0:
                # dispara o projétil a partir do bico da nave
                projeteis.append(Projetil(nave.x + nave.largura // 2, nave.y))
            if evento.key == pygame.K_RETURN and estado_jogo == ESTADO_PAUSADO: 
                # libera o início da fase que está aguardando
                if tempo_inicio_partida is None:
                    tempo_inicio_partida = pygame.time.get_ticks()
                estado_jogo = ESTADO_JOGANDO

    # atualização de lógica (caso o jogo não tenha acabado)
    if estado_jogo == ESTADO_JOGANDO:
        nave.mover(teclas)

        # criar novas letras na tela periodicamente
        tempo_spawn += 1
        if tempo_spawn > intervalo_spawn:
            letras.append(LetraFlutuante(letras_restantes, chance_letra_certa, multiplicador_velocidade))
            tempo_spawn = 0

        # movimentação dos projéteis
        for p in projeteis[:]:
            p.mover()
            if p.y < 0:
                projeteis.remove(p)

        # movimentação e limpeza das letras
        for l in letras[:]:
            l.mover()
            # remove letras que saíram da tela ou cujo tempo de feedback acabou
            if l.y > altura:
                letras.remove(l)
            elif l.estado != "normal" and l.cronometro_estado <= 0:
                letras.remove(l)

        # sistema de colisão e validação
        for p in projeteis[:]:
            for l in letras[:]:
                if l.estado == "normal" and l.obter_retangulo().collidepoint(p.x, p.y):
                    # remove o projeto que colidiu
                    if p in projeteis: projeteis.remove(p)

                    # valida se é a letra correta que o aluno precisava acertar
                    if l.caractere == letras_restantes[0]:
                        l.estado = "correto"
                        l.cronometro_estado = 20 # exibe por 20 frames
                        som_acerto.play()
                        letras_acertadas.append(letras_restantes.pop(0))
                    else:
                        l.estado = "incorreto"
                        l.cronometro_estado = 20
                        som_erro.play()

        # a palavra da fase foi concluída?
        if not letras_restantes:
            fase_recem_concluida = fase_atual # guarda qual fase acabou de ser vencida
            letras = []
            projeteis = []
            if fase_atual + 1 < len(fases):
                iniciar_fase(fase_atual + 1) # prepara a próxima fase
                estado_jogo = ESTADO_PAUSADO
            else: 
                duracao_partida = (pygame.time.get_ticks() - tempo_inicio_partida) / 1000
                log_final = (
                    f"Fases concluídas: {len(fases)}/{len(fases)}\n"
                    f"Movimentos: esquerda={contagem_teclas[pygame.K_LEFT]} | "
                    f"direita={contagem_teclas[pygame.K_RIGHT]}\n"
                    f"Disparos (espaço): {contagem_teclas[pygame.K_SPACE]}"
                )
                try:
                    registrar_vitoria(duracao_partida, log_final)
                except (OSError, sqlite3.Error) as erro:
                    erro_banco = str(erro)
                estado_jogo = ESTADO_VITORIA

    # renderização / desenhos
    # 0- indicador de fase (canto superior esquerdo)
    texto_fase  = fonte_pequena.render(f"FASE {fase_atual + 1} / {len(fases)}", True, branco)
    tela.blit(texto_fase, (20, 20))

    # 1- desenha frase alvo (central superior)
    # monta a string visual mostrando o progresso do aluno (ex: "A B_ _ _")
    string_progresso = ""
    indice_letras_acertadas = 0

    for caractere in frase_alvo:
        if caractere == " ":
            string_progresso += "  "
        elif indice_letras_acertadas < len(letras_acertadas) and caractere == letras_acertadas[indice_letras_acertadas]:
            string_progresso += caractere + " "
            indice_letras_acertadas += 1
        else:
            string_progresso += "_ "

    texto_frase = fonte_gigante.render(string_progresso, True, amarelo)
    rect_frase = texto_frase.get_rect(center=(largura // 2, 50))
    tela.blit(texto_frase, rect_frase)

    # 2- desenha elementos do jogo
    for l in letras: l.desenhar(tela)
    for p in projeteis: p.desenhar(tela)
    nave.desenhar(tela)

    linhas_controles = [
        (f"> (move para direita): {contagem_teclas[pygame.K_RIGHT]}", amarelo),
        (f"< (move para esquerda): {contagem_teclas[pygame.K_LEFT]}", amarelo),
        (f"Espaço (dispara): {contagem_teclas[pygame.K_SPACE]}", amarelo),
    ]
    for indice, (linha, cor) in enumerate(linhas_controles):
        texto_controle = fonte_controles.render(linha, True, cor)
        tela.blit(texto_controle, (20, 85 + indice * 24))

    # 3- mensagens de pausa / vitória final
    if estado_jogo == ESTADO_PAUSADO:
        y_base = altura // 2 - 60

        # se uma fase anterior acabou de ser concluída, mostra a mensagem de parabéns
        if fase_recem_concluida is not None: 
            texto_concluida = fonte_gigante.render(f"FASE {fase_recem_concluida + 1} CONCLUÍDA!", True, verde)
            rect_concluida = texto_concluida.get_rect(center=(largura // 2, y_base))
            tela.blit(texto_concluida, rect_concluida)
            y_base += 60

        texto_prox = fonte_media.render(f"Fase {fase_atual + 1}: {frase_alvo}", True, branco)
        rect_prox = texto_prox.get_rect(center=(largura // 2, y_base))
        tela.blit(texto_prox, rect_prox)

        # texto "pressione ENTER" com um leve efeito de pulsar
        intensidade = int(150 + 105 * abs(math.sin(pygame.time.get_ticks() / 300)))
        texto_instrucao = fonte_media.render("Pressione ENTER para começar", True, (intensidade, intensidade, 0))
        rect_instrucao = texto_instrucao.get_rect(center=(largura // 2, y_base + 60))
        tela.blit(texto_instrucao, rect_instrucao)

    elif estado_jogo == ESTADO_VITORIA:
        texto_vitoria = fonte_gigante.render("PARABÉNS! VOCÊ VENCEU!", True, verde)
        rect_vitoria = texto_vitoria.get_rect(center=(largura // 2, altura // 2 - 90))
        tela.blit(texto_vitoria, rect_vitoria)
        texto_tempo = fonte_media.render(
            f"Tempo total: {formatar_duracao(duracao_partida)}", True, branco
        )
        rect_tempo = texto_tempo.get_rect(center=(largura // 2, altura // 2 - 25))
        tela.blit(texto_tempo, rect_tempo)

        for indice, linha in enumerate(log_final.splitlines()):
            texto_log = fonte_pequena.render(linha, True, amarelo)
            rect_log = texto_log.get_rect(center=(largura // 2, altura // 2 + 15 + indice * 30))
            tela.blit(texto_log, rect_log)

        if erro_banco:
            texto_status = fonte_controles.render(
                f"Erro ao salvar o resultado: {erro_banco[:80]}", True, (255, 50, 50)
            )
        else:
            texto_status = fonte_controles.render("Resultado salvo no banco de dados.", True, verde)
        rect_status = texto_status.get_rect(center=(largura // 2, altura // 2 + 115))
        tela.blit(texto_status, rect_status)

    # atualiza a tela
    pygame.display.flip()
    relogio.tick(60) # mantém o jogo a 60fps

pygame.quit()