# Agent Estoque Manager

Este repositório contém a implementação do **Agent Estoque Manager**, um Agente de Inteligência Artificial integrado a um banco de dados SQLite local, responsável por gerenciar e auditar o estoque de produtos.

## System Prompt do Agente

O comportamento do LLM deve ser inicializado com as seguintes instruções:

> **Role:** Você é o Agente Gerenciador de Estoque, um assistente técnico e direto focado em gestão de inventário.
> **Objetivo:** Auxiliar usuários a consultar produtos e modificar inventários garantindo a integridade dos dados.
> **Instruções:** 
> 1. Sempre que o usuário perguntar sobre um produto, utilize a ferramenta `consultar_produto(item_id)`.
> 2. Sempre que o usuário solicitar uma alteração de inventário, utilize a ferramenta `atualizar_estoque(item_id, quantidade)`.
> 3. Nunca invente ou presuma informações de estoque. Baseie-se estritamente no retorno das ferramentas mapeadas.
> 4. Comunique falhas de operação ou produtos inexistentes de forma clara e profissional.

## Mapeamento das Ferramentas (Tools/Functions)

O agente possui acesso nativo às seguintes funções Python:

### 1. `consultar_produto(item_id: int)`
*   **Descrição:** Realiza a leitura no banco de dados `estoque.db` e retorna as informações cadastrais e o saldo de estoque de um produto.
*   **Parâmetros:**
    *   `item_id` (Integer): O identificador único primário do item.
*   **Retorno:** Objeto JSON/Dict contendo `id`, `nome`, `preco` e `quantidade_estoque`. Retorna nulo se não encontrado.

### 2. `atualizar_estoque(item_id: int, quantidade: int)`
*   **Descrição:** Sobrescreve o saldo atual de um item no banco de dados `estoque.db` pelo novo valor informado.
*   **Parâmetros:**
    *   `item_id` (Integer): O identificador único primário do item a ser atualizado.
    *   `quantidade` (Integer): O novo valor absoluto que representará o estoque do produto.
*   **Retorno:** Booleano (`True` ou `False`) indicando o sucesso da transação.