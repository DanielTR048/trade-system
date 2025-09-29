📜 Visão Geral do Projeto

Este projeto é um serviço de backend (API REST) completo para executar simulações e backtests de estratégias de trading do tipo trend following. O sistema utiliza dados históricos do Yahoo Finance, integra o poderoso framework backtrader para a execução das simulações, e persiste todos os dados e resultados em um banco de dados PostgreSQL.

O objetivo é fornecer uma plataforma robusta e flexível para validar a eficácia de diferentes estratégias de investimento, incluindo a aplicação de um filtro baseado em Machine Learning para otimizar os sinais de entrada. Toda a arquitetura foi containerizada com Docker para garantir a facilidade de instalação e a reprodutibilidade do ambiente.

✨ Funcionalidades Principais
API RESTful Completa: Endpoints para rodar backtests, consultar resultados, listar execuções e atualizar dados de mercado.

Integração com Yahoo Finance: Coleta e armazenamento de dados históricos (OHLCV) para qualquer ticker disponível na plataforma.

Múltiplas Estratégias de Trading:

Cruzamento de Médias Móveis (SMA Cross): Estratégia clássica de seguidora de tendência.

Breakout (Rompimento): Baseada em canais de Donchian para identificar rompimentos de máximas e mínimas.

Momentum: Opera com base na taxa de variação (ROC) do preço em um período definido.

Parâmetros Dinâmicos: Todas as estratégias podem ser configuradas dinamicamente via API, permitindo testar diferentes parâmetros (períodos de médias, janelas de breakout, etc.) sem alterar o código.

Gestão de Risco Profissional:

Position Sizing: Cálculo automático do tamanho da posição para limitar o risco por operação a 1% do capital total.

Stop Loss: Utilização do indicador de volatilidade ATR para definir um stop loss dinâmico em cada operação.

Filtro com Machine Learning: Um modelo de Regressão Logística pode ser treinado e utilizado como um filtro para validar os sinais de compra, visando melhorar a taxa de acerto da estratégia.

Persistência de Dados: Todos os tickers, preços, backtests, métricas e trades são salvos em um banco de dados PostgreSQL, com schema gerenciado por Alembic.

Análise e Visualização: Inclui um Jupyter Notebook para se conectar ao banco, carregar os resultados de um backtest e gerar gráficos interativos (Preço x Trades, Curva de Capital, etc.).

Automação: Um script de "cron job" para atualização diária e automática dos dados de mercado de todos os tickers cadastrados.

🛠️ Tecnologias Utilizadas
Backend: Python 3.12, FastAPI

Motor de Backtesting: Backtrader

Banco de Dados: PostgreSQL

ORM e Migrações: SQLAlchemy, Alembic

Análise de Dados: Pandas, Numpy

Machine Learning: Scikit-learn, Joblib

Fonte de Dados: Yfinance

Testes: Pytest, Pytest-Mock

Containerização: Docker e Docker Compose

🚀 Como Executar o Projeto
Graças ao Docker, a configuração do ambiente é extremamente simples e requer apenas o Docker Desktop instalado.

Clone o Repositório:

git clone https://github.com/DanielTR048/trade-system.git
cd trade-system
Configure as Variáveis de Ambiente:

Renomeie o arquivo .env.example para .env.

Se desejar, altere a senha padrão POSTGRES_PASSWORD e atualize a DATABASE_URL com a mesma senha.

Inicie os Serviços com Docker Compose:
Este comando irá construir a imagem da aplicação (instalando todas as dependências) e iniciar os containers da API e do banco de dados em segundo plano.

docker-compose up -d --build

Execute as Migrações do Banco de Dados:
Com os containers rodando, execute este comando para criar todas as tabelas no banco de dados.

docker-compose run --rm app alembic upgrade head

Pronto! A API está no ar!

Acesse a documentação interativa (Swagger UI) em: http://localhost:8000/docs

O serviço do banco de dados está acessível em: localhost:5432

⚙️ Como Usar a API
O fluxo de uso recomendado é:

Carregar os Dados Históricos:

Use o endpoint POST /data/update/{ticker} para baixar e salvar os dados de um ativo.

Exemplo: POST /data/update/PETR4.SA

(Opcional) Treinar um Modelo de ML:

Se quiser usar uma estratégia com filtro de ML, treine o modelo primeiro.

Exemplo: POST /ml/train/PETR4.SA

Executar um Backtest:

Use o endpoint POST /backtests/run.

No corpo da requisição, especifique o ticker, as datas, a estratégia e, opcionalmente, os parâmetros.

Exemplo de corpo (body) da requisição:

JSON

{
  "ticker": "PETR4.SA",
  "start_date": "2021-01-01",
  "end_date": "2024-12-31",
  "initial_cash": 100000,
  "strategy_type": "sma_cross_ml",
  "strategy_params": {
    "fast_length": 15,
    "slow_length": 60
  }
}
Consultar os Resultados:

A resposta do passo anterior incluirá um backtest_id.

Use o endpoint GET /backtests/{backtest_id}/results para ver os detalhes completos, incluindo métricas e a lista de trades.

Use o endpoint GET /backtests para listar todas as execuções.

📈 Visualização e Análise
O projeto inclui um Jupyter Notebook para análises visuais.

Crie e ative um ambiente virtual local:

python -m venv venv
.\venv\Scripts\activate

Instale as dependências de análise:

pip install jupyterlab pandas plotly sqlalchemy psycopg2-binary

Inicie o JupyterLab:

jupyter lab

Abra o notebook em notebooks/results_visualization.ipynb e siga as instruções para gerar os gráficos.

🧪 Testes
Os testes automatizados foram escritos com Pytest e garantem a lógica principal da aplicação. Para executá-los:

Crie/ative o ambiente virtual de testes (se ainda não o fez) e instale os requisitos:

py -3.12 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

Execute o Pytest:

pytest

Para ver o relatório de cobertura de testes:

pytest --cov=app