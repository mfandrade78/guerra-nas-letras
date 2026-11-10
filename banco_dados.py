import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path


def _obter_caminho_banco():
    pasta_dados = os.getenv("LOCALAPPDATA")
    if pasta_dados:
        return Path(pasta_dados) / "GuerraNasLetras" / "resultados.db"
    return Path.home() / ".guerra-nas-letras" / "resultados.db"


CAMINHO_BANCO = _obter_caminho_banco()


def registrar_vitoria(duracao_segundos, log_final, caminho=CAMINHO_BANCO):
    """Persiste a duracao e o log de uma partida concluida."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(caminho)) as conexao:
        with conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS vitorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concluida_em TEXT NOT NULL,
                    duracao_segundos REAL NOT NULL,
                    log_final TEXT NOT NULL
                )
                """
            )
            conexao.execute(
                """
                INSERT INTO vitorias (concluida_em, duracao_segundos, log_final)
                VALUES (?, ?, ?)
                """,
                (datetime.now().astimezone().isoformat(timespec="seconds"),
                 duracao_segundos, log_final),
            )
