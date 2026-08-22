import sqlite3
import logging
from typing import Optional, Dict, Union

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Mantemos na raiz do projeto. Ele será recriado a cada reinício do Render.
DB_PATH = 'estoque.db' 

def inicializar_banco_de_dados() -> None:
    """
    Cria a tabela 'produtos' no banco SQLite e insere dados de teste,
    caso a tabela ainda não exista.
    """
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
            
            # Inserção de dados de teste (apenas se a tabela estiver vazia)
            cursor.execute("SELECT COUNT(*) FROM produtos")
            if cursor.fetchone()[0] == 0:
                produtos_teste = [
                    (1, 'Notebook Pro', 4500.00, 15),
                    (2, 'Mouse sem fio', 120.50, 50),
                    (3, 'Teclado Mecânico', 350.00, 30)
                ]
                cursor.executemany("""
                    INSERT INTO produtos (id, nome, preco, quantidade_estoque) 
                    VALUES (?, ?, ?, ?)
                """, produtos_teste)
                logging.info("Dados de teste inseridos com sucesso.")
            
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")

def consultar_produto(item_id: int) -> Optional[Dict[str, Union[int, str, float]]]:
    """
    Consulta as informações de um produto específico no banco de dados.

    Args:
        item_id (int): O identificador único do produto.

    Returns:
        dict: Um dicionário com os dados do produto (id, nome, preco, quantidade_estoque).
        None: Se o produto não for encontrado ou ocorrer um erro.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # Permite acessar as colunas por nome
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (item_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                return dict(resultado)
            else:
                logging.warning(f"Produto com ID {item_id} não encontrado.")
                return None
    except sqlite3.Error as e:
        logging.error(f"Erro ao consultar produto (ID: {item_id}): {e}")
        return None

def atualizar_estoque(item_id: int, quantidade: int) -> bool:
    """
    Atualiza a quantidade em estoque de um produto específico.

    Args:
        item_id (int): O identificador único do produto.
        quantidade (int): A nova quantidade total em estoque.

    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Verifica se o produto existe antes de atualizar
            cursor.execute("SELECT id FROM produtos WHERE id = ?", (item_id,))
            if not cursor.fetchone():
                logging.warning(f"Falha na atualização: Produto com ID {item_id} não existe.")
                return False
                
            cursor.execute("""
                UPDATE produtos 
                SET quantidade_estoque = ? 
                WHERE id = ?
            """, (quantidade, item_id))
            
            conn.commit()
            logging.info(f"Estoque do produto {item_id} atualizado para {quantidade} unidades.")
            return True
    except sqlite3.Error as e:
        logging.error(f"Erro ao atualizar estoque (ID: {item_id}): {e}")
        return False

# Execução principal para inicialização e testes locais
if __name__ == "__main__":
    inicializar_banco_de_dados()
    
    # Exemplo de uso das ferramentas
    print(consultar_produto(1))
    atualizar_estoque(1, 20)
    print(consultar_produto(1))