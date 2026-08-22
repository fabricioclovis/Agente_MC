import logging
import os
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Optional, Union

# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Caminho do banco de dados na raiz do projeto
DB_PATH = 'estoque.db'


def inicializar_banco_de_dados() -> None:
    """Cria a tabela 'produtos' no SQLite e insere dados de teste se a tabela estiver vazia."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    quantidade_estoque INTEGER NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM produtos")
            if cursor.fetchone()[0] == 0:
                produtos_teste = [
                    (1, 'Notebook Pro', 4500.00, 15),
                    (2, 'Mouse sem fio', 120.50, 50),
                    (3, 'Teclado Mecanico', 350.00, 30),
                ]
                cursor.executemany("""
                    INSERT INTO produtos (id, nome, preco, quantidade_estoque) 
                    VALUES (?, ?, ?, ?)
                """, produtos_teste)
                logging.info("Dados de teste inseridos com sucesso.")

            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")


def consultar_produto(
    item_id: int,
) -> Optional[Dict[str, Union[int, str, float]]]:
    """Consulta um produto especifico pelo seu ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (item_id,))
            resultado = cursor.fetchone()

            if resultado:
                return dict(resultado)
            else:
                logging.warning(f"Produto com ID {item_id} nao encontrado.")
                return None
    except sqlite3.Error as e:
        logging.error(f"Erro ao consultar produto (ID: {item_id}): {e}")
        return None


def atualizar_estoque(item_id: int, quantidade: int) -> bool:
    """Atualiza a quantidade em estoque de um produto."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM produtos WHERE id = ?", (item_id,))
            if not cursor.fetchone():
                logging.warning(
                    f"Falha: Produto com ID {item_id} nao existe."
                )
                return False

            cursor.execute(
                """
                UPDATE produtos 
                SET quantidade_estoque = ? 
                WHERE id = ?
            """,
                (quantidade, item_id),
            )

            conn.commit()
            logging.info(
                f"Estoque do produto {item_id} atualizado para {quantidade} unidades."
            )
            return True
    except sqlite3.Error as e:
        logging.error(f"Erro ao atualizar estoque (ID: {item_id}): {e}")
        return False


def iniciar_servidor_web() -> None:
    """Inicia um servidor HTTP simples para manter a aplicacao ativa no Render."""
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    logging.info(f"Servidor web ativo na porta {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    # 1. Cria a base e insere os dados
    inicializar_banco_de_dados()

    # 2. Executa testes de leitura e atualizacao
    print(consultar_produto(1))
    atualizar_estoque(1, 20)
    print(consultar_produto(1))

    # 3. Mantem o processo rodando para o Render (sempre no final)
    iniciar_servidor_web()