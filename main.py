import logging
import sqlite3
from typing import Dict, Optional, Union
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
DB_PATH = 'estoque.db'

app = FastAPI(title="McDonald's Estoque Manager")


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
            produtos_mcdonalds = [
                (1, 'Big Mac', 29.90, 50),
                (2, 'McFritas Grande', 14.90, 120),
                (3, 'Coca-Cola 500ml', 10.90, 80),
                (4, 'McFlurry M&Ms', 16.90, 40),
            ]
            cursor.executemany("""
                INSERT INTO produtos (id, nome, preco, quantidade_estoque) 
                VALUES (?, ?, ?, ?)
            """, produtos_mcdonalds)
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


ESTILO_MCDONALDS = """
<style>
    body { font-family: 'Arial', sans-serif; background-color: #27251F; margin: 0; padding: 20px; color: #333; }
    .card { max-width: 480px; background: white; margin: 30px auto; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 16px rgba(0,0,0,0.4); border: 3px solid #FFC72C; }
    .header { background-color: #DA291C; padding: 20px; text-align: center; color: #FFC72C; }
    .header h1 { margin: 0; font-size: 28px; text-shadow: 1px 1px 2px #000; font-weight: bold; }
    .content { padding: 25px; background: #FFF; }
    input { width: 100%; padding: 12px; margin: 10px 0; box-sizing: border-box; border: 2px solid #DDD; border-radius: 6px; font-size: 16px; }
    button { width: 100%; background-color: #FFC72C; color: #27251F; padding: 14px; border: none; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 16px; text-transform: uppercase; transition: 0.2s; }
    button:hover { background-color: #e6b020; }
    .badge { background: #DA291C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 14px; display: inline-block; }
    a { display: block; text-align: center; margin-top: 15px; color: #DA291C; font-weight: bold; text-decoration: none; }
    a:hover { text-decoration: underline; }
</style>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>McEstoque - McDonald's</title>
        {ESTILO_MCDONALDS}
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>🍟 McEstoque</h1>
                <p style="margin: 5px 0 0 0; color: white;">Sistema de Controle do Cardápio</p>
            </div>
            <div class="content">
                <h2>🔍 Buscar Produto no Cardápio</h2>
                <form action="/buscar" method="post">
                    <label>Informe o ID do Produto (1: Big Mac, 2: McFritas, 3: Refri, 4: McFlurry):</label>
                    <input type="number" name="item_id" required placeholder="ID do produto">
                    <button type="submit">Consultar Estoque</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/buscar", response_class=HTMLResponse)
def buscar(item_id: int = Form(...)):
    produto = consultar_produto(item_id)

    if produto:
        resultado_html = f"""
        <div style="background: #FFF8E7; border-left: 5px solid #FFC72C; padding: 15px; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #DA291C;">🍔 {produto['nome']}</h3>
            <p><strong>ID:</strong> <span class="badge">#{produto['id']}</span></p>
            <p><strong>Preço:</strong> R$ {produto['preco']:.2f}</p>
            <p><strong>Estoque no Restaurante:</strong> <span style="font-size: 18px; color: #DA291C; font-weight: bold;">{produto['quantidade_estoque']} un</span></p>
        </div>

        <h3 style="color: #27251F;">✏️ Atualizar Estoque</h3>
        <form action="/atualizar" method="post">
            <input type="hidden" name="item_id" value="{produto['id']}">
            <input type="number" name="quantidade" placeholder="Digite o novo saldo" required>
            <button type="submit" style="background-color: #DA291C; color: white;">Salvar Novo Estoque</button>
        </form>
        """
    else:
        resultado_html = "<p style='color: #DA291C; font-weight: bold;'>❌ Produto não encontrado no cardápio do McDonald's!</p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultado - McEstoque</title>
        {ESTILO_MCDONALDS}
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>🍟 McEstoque</h1>
            </div>
            <div class="content">
                {resultado_html}
                <a href="/">← Voltar para a busca</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/atualizar", response_class=HTMLResponse)
def atualizar(item_id: int = Form(...), quantidade: int = Form(...)):
    sucesso = atualizar_estoque(item_id, quantidade)
    msg = (
        "✅ Estoque do McDonald's atualizado com sucesso!"
        if sucesso
        else "❌ Falha ao atualizar estoque."
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Status - McEstoque</title>
        {ESTILO_MCDONALDS}
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>🍟 McEstoque</h1>
            </div>
            <div class="content" style="text-align: center;">
                <h3 style="color: #27251F;">{msg}</h3>
                <a href="/">← Voltar ao Início</a>
            </div>
        </div>
    </body>
    </html>
    """