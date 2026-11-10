# guerra-nas-letras
Um jogo de 64bits em 2D para auxiliar meus alunos do ensino fundamental em seu processo de alfabetização.

# Como Jogar
Se quiser apenas jogar, basta abrir a pasta dist e instalar o arquivo Guerra_nas_Letras.exe

Use as setas esquerda e direita para mover a nave e a barra de espaço para disparar. O painel do jogo mostra quantas vezes cada tecla foi pressionada.

Ao concluir todas as fases, o jogo exibe o tempo total da partida e um log com as fases concluídas e o uso dos controles. O resultado é gravado em um banco SQLite (`resultados.db`), em `%LOCALAPPDATA%\GuerraNasLetras` no Windows (ou em `~/.guerra-nas-letras` se essa variável não existir). Cada vitória é armazenada na tabela `vitorias`, com data/hora, duração em segundos e log final.
