import logging
import sqlite3
from typing import Dict, Optional, Union
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
DB_PATH = 'estoque.db'

app = FastAPI()


def inicializar_banco_de_dados() -> None:
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
            conn.commit()


@app.on_event("startup")
def startup_event():
    inicializar_banco_de_dados()


def consultar_produto(
    item_id: int,
) -> Optional[Dict[str, Union[int, str, float]]]:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (item_id,))
            resultado = cursor.fetchone()
            return dict(resultado) if resultado else None
    except sqlite3.Error as e:
        logging.error(f"Erro ao consultar: {e}")
        return None


def atualizar_estoque(item_id: int, quantidade: int) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produtos SET quantidade_estoque = ? WHERE id = ?",
                (quantidade, item_id),
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Erro ao atualizar: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gerenciador de Estoque</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
            .container { max-width: 500px; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: auto; }
            input, button { padding: 12px; margin: 8px 0; width: 100%; box-sizing: border-box; border-radius: 4px; border: 1px solid #ccc; }
            button { background-color: #28a745; color: white; border: none; font-weight: bold; cursor: pointer; }
            button:hover { background-color: #218838; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔍 Pesquisar Produto</h2>
            <form action="/buscar" method="post">
                <label>Digite o ID do Produto (ex: 1, 2, 3):</label>
                <input type="number" name="item_id" required placeholder="ID do produto">
                <button type="submit">Buscar no Estoque</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/buscar", response_class=HTMLResponse)
def buscar(item_id: int = Form(...)):
    produto = consultar_produto(item_id)

    if produto:
        card = f"""
        <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 15px;">
            <h3>📦 {produto['nome']}</h3>
            <p><strong>ID:</strong> {produto['id']}</p>
            <p><strong>Preço:</strong> R$ {produto['preco']:.2f}</p>
            <p><strong>Quantidade em Estoque:</strong> {produto['quantidade_estoque']} unidades</p>
            <hr>
            <h4>✏️ Atualizar Estoque</h4>
            <form action="/atualizar" method="post">
                <input type="hidden" name="item_id" value="{produto['id']}">
                <input type="number" name="quantidade" placeholder="Nova quantidade" required>
                <button type="submit" style="background-color: #007bff;">Salvar Nova Quantidade</button>
            </form>
        </div>
        """
    else:
        card = "<p style='color: red;'>❌ Produto não encontrado no banco de dados.</p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultado</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
            .container {{ max-width: 500px; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: auto; }}
            input, button {{ padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }}
            button {{ color: white; border: none; font-weight: bold; cursor: pointer; }}
            a {{ display: inline-block; margin-top: 15px; color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Resultado da Pesquisa</h2>
            {card}
            <a href="/">← Voltar para a Pesquisa</a>
        </div>
    </body>
    </html>
    """


@app.post("/atualizar", response_class=HTMLResponse)
def atualizar(item_id: int = Form(...), quantidade: int = Form(...)):
    sucesso = atualizar_estoque(item_id, quantidade)
    msg = (
        "✅ Estoque atualizado com sucesso!"
        if sucesso
        else "❌ Falha ao atualizar."
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
            .container {{ max-width: 500px; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: auto; }}
            a {{ display: inline-block; margin-top: 15px; color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>{msg}</h3>
            <a href="/">← Voltar para a Pesquisa</a>
        </div>
    </body>
    </html>
    """