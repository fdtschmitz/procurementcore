# Portal de Compras - Integração TOTVS RM

Um portal web escalável desenvolvido em **Python (Flask)** para atuar como uma interface amigável (estilo e-commerce) para a criação e acompanhamento de Solicitações de Compra no ERP **TOTVS RM**.

O objetivo do projeto é descentralizar e simplificar o fluxo de suprimentos, permitindo que os colaboradores consultem um catálogo homologado de produtos, adicionem itens ao carrinho, informem o Centro de Custo e enviem o pedido diretamente para o ERP de forma rápida e rastreável.

---

## 🏗 Arquitetura do Projeto

Para garantir performance e não sobrecarregar as APIs nativas do TOTVS RM, a aplicação adota uma estratégia de **Cache Local Sincronizado**:

1. **Banco de Dados Local (SQLite/PostgreSQL):** Produtos, Centros de Custo e o histórico de Solicitações de Compra ficam cacheados em um banco de dados relacional gerido pelo SQLAlchemy.
2. **Consultas Customizadas:** A carga de dados e a atualização Delta utilizam sentenças SQL otimizadas no RM para trazer apenas o que foi alterado (evitando tráfego desnecessário).
3. **Drafts (Rascunhos):** Enquanto o usuário navega na loja e preenche o carrinho, tudo é salvo apenas no banco de dados local. A requisição para o ERP ocorre somente no momento do "Checkout".
4. **Autenticação Server-Side:** Utiliza o endpoint nativo do RM. O backend gerencia o ciclo de vida do Token JWT (Bearer). Como a expiração ocorre em apenas 5 minutos, a aplicação possui um interceptor que utiliza o `refresh_token` (duração de 16h) de forma transparente para renovar o acesso do usuário sem interromper sua navegação.

### Padrão de Projeto
O código segue o padrão **Application Factory** com separação em **Blueprints**, o que isola regras de negócios, rotas, modelos e comandos de sincronização, facilitando a manutenção e a escalabilidade da equipe.

---

## 🛠 Tecnologias Utilizadas

* **Backend:** Python 3, Flask, Blueprint routing.
* **Banco de Dados / ORM:** SQLAlchemy, SQLite (preparado para migração fácil para PostgreSQL/SQL Server).
* **Integração TOTVS RM:** Biblioteca `requests` consumindo REST API (Endpoints de Autenticação e Consulta SQL).
* **Frontend:** Jinja2 Templates, HTML5, CSS3, Vanilla Javascript (comunicação assíncrona com `fetch`).
* **Servidor de Produção (Previsto):** Waitress (WSGI).

---

## 📂 Estrutura de Diretórios

```text
procurement_core/
├── app/
│   ├── __init__.py             # Application Factory
│   ├── config.py               # Configurações globais e carregamento de segredos
│   ├── extensions.py           # Instanciação do SQLAlchemy, Migrate, etc.
│   ├── models/                 # Modelagem de Dados
│   │   ├── costcenter.py       # Tabela de Centros de Custo
│   │   ├── product.py          # Tabela de Produtos homologados
│   │   └── request.py          # Tabelas de Solicitações (Histórico e Rascunhos do Carrinho)
│   ├── routes/                 # Controladores (Blueprints)
│   │   ├── auth.py             # Login, Logout e controle de Sessão
│   │   ├── store.py            # Loja, Carrinho e Dashboard do Usuário
│   │   ├── buyer.py            # [Em breve] Visão do Comprador
│   │   └── admin.py            # [Em breve] Visão do Administrador
│   ├── services/
│   │   ├── totvs_api.py        # Centralização das chamadas HTTP genéricas ao RM
│   │   └── totvs_auth.py       # Regras de Autenticação e Refresh Token
│   ├── utils/
│   │   └── auth.py             # Decoradores (@login_required)
│   └── tasks/
│       └── sync_tasks.py       # Rotinas de ETL/Carga do RM para o Banco Local
├── static/
│   └── img/produtos/           # Repositório de imagens dos produtos (nomenclatura: codigo.jpg)
├── templates/                  # Interfaces da aplicação (Login, Dashboard, Loja, Carrinho)
├── secrets.json                # (Ignorado no Git) Credenciais da API e sentenças SQL
├── sync.py                     # Script para gatilho manual da carga de dados
└── run.py                      # Ponto de entrada do servidor de desenvolvimento (Flask/Waitress)
```

## 🚀Como Executar Localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o arquivo secrets.json:
Crie o arquivo na raiz do projeto contendo as URLs da sua coligada, usuário de integração e os identificadores das Consultas SQL customizadas.

3. Execute a carga de dados inicial (Cria o Banco e Popula):
```bash
python sync.py
```

4. Inicie o servidor:
```Bash
python run.py
```

Acesse http://localhost:5000 (ou o IP da sua máquina na rede).

## 🗺️Roadmap para Produção (Go-Live)

O projeto está sendo construído em fases. Abaixo estão as atividades pendentes antes do lançamento oficial.
🟢 Fase 1: Estrutura, Carga e Loja (Concluído)

    [x] Definição da arquitetura Flask Factory e Blueprints.

    [x] Configuração da autenticação e renovação automática de Bearer Tokens (TOTVS RM).

    [x] Criação das Consultas SQL no RM (INTER.001.X) e carga local (Produtos, Centros de Custo, Cabeçalho e Itens de Solicitações).

    [x] Dashboard de acompanhamento com visão em Accordion.

    [x] Catálogo de Produtos (Loja) com paginação, filtros e alternância de layout (Bloco/Lista).

    [x] Carrinho de compras local (Persistência no banco via requisições assíncronas).

🟡 Fase 2: Checkout e Integração

    [ ] Finalizar Pedido: Mapear os dados do RequestDraft e disparar um POST para o endpoint /api/mov/v1/Movements (Movimento 1.1.04) passando o Access Token do usuário logado.

    [ ] Limpeza Pós-Envio: Apagar o carrinho após sucesso do RM e redirecionar para tela de sucesso com o NUMEROMOV retornado pela API.

    [ ] Tratamento de Erros de Integração: Exibir mensagens claras ao usuário caso o RM rejeite o payload (ex: restrição orçamentária, quantidade inválida).

🔵 Fase 3: Módulos Adicionais (Negócio)

    [ ] Módulo do Administrador: Tela protegida para forçar a sincronização de dados sob demanda e visualizar logs de erros.

    [ ] Módulo do Comprador: Painel para visão macro de todas as solicitações pendentes de aprovação e cotação.

    [ ] Homologação de Novos Produtos: Fluxo para o usuário sugerir um novo produto (anexando PDF/descritivo) caso não o encontre na loja.

🟣 Fase 4: Automação (Background Jobs)

    [ ] Atualização Delta Automática: Implementar Celery + Redis (ou APScheduler/Cron) para rodar o script de sincronização a cada X horas, buscando apenas registros novos (DATA_ULTIMA_SYNC).

🔴 Fase 5: Deploy e Infraestrutura (Go-Live)

    [ ] Substituir o servidor de desenvolvimento do Flask pelo Waitress (já testado localmente) ou Gunicorn para suporte a múltiplas conexões concorrentes.

    [ ] Avaliar a migração do banco SQLite para PostgreSQL ou SQL Server visando maior confiabilidade concorrencial.

    [ ] Configuração de Proxy Reverso (Nginx/IIS/Apache) para gestão de certificados SSL (HTTPS).