# guerra-nas-letras
Um jogo de 64bits em 2D para auxiliar meus alunos do ensino fundamental em seu processo de alfabetização.

# Como Jogar
Se quiser apenas jogar, basta abrir a pasta dist e instalar o arquivo Guerra_nas_Letras.exe

Use as setas esquerda e direita para mover a nave e a barra de espaço para disparar. O painel do jogo mostra quantas vezes cada tecla foi pressionada.

Ao concluir todas as fases, o jogo exibe o tempo total da partida e um log com as fases concluídas e o uso dos controles. O resultado é gravado em um banco SQLite (`resultados.db`), em `%LOCALAPPDATA%\GuerraNasLetras` no Windows (ou em `~/.guerra-nas-letras` se essa variável não existir). Cada vitória é armazenada na tabela `vitorias`, com data/hora, duração em segundos e log final.

# Atualização do executável
Ao enviar alterações para a branch `main`, o GitHub Actions compila o jogo no Windows e atualiza `dist/Guerra_nas_Letras.exe` com o código mais recente. O commit do executável não inicia outro build. Também é possível iniciar a compilação manualmente pela aba **Actions**, usando o workflow **Build Windows executable**.

O workflow precisa de permissão de escrita no conteúdo do repositório para publicar o executável. Se o commit automático falhar por permissão, habilite a permissão de leitura e escrita para `GITHUB_TOKEN` nas configurações de Actions do repositório.
