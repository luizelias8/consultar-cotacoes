# Sistema de Consulta de Cotações com Alerta por E-mail

Este projeto é um sistema de consulta automática de cotações de ações da bolsa brasileira (B3) e envia alertas por e-mail quando os preços atingem valores predefinidos. O agendamento das consultas é configurável, assim como os parâmetros de conexão com o banco de dados e o servidor de e-mail.

## Funcionalidades

- Consulta cotações de ações usando a biblioteca `yfinance`.
- Armazena as cotações em um banco de dados PostgreSQL.
- Envia alertas por e-mail quando o preço de uma ação atingir ou ficar abaixo do valor configurado.
- O intervalo de consulta é configurável via arquivo `configuracoes.json`.
- Suporte a múltiplos tickers de ações da B3 (ex: WEGE3.SA, PETR4.SA).

## Requisitos

- Python 3.7+
- PostgreSQL
- Bibliotecas Python:
  - `yfinance`
  - `psycopg2`
  - `schedule`
  - `smtplib`
  - `json`

## Instalação

1. Clone este repositório:

    ```bash
    git clone https://github.com/luizelias8/consultar-cotacoes.git
    cd consultar-cotacoes

2. Instale as dependências necessárias:

    ```bash
    pip install requirements.txt
    ```

Antes de executar o projeto, você deve criar o arquivo `configuracoes.json` com base no arquivo de exemplo fornecido.

Copie o arquivo de exemplo `configuracoes-exemplo.json` e renomeie-o para `configuracoes.json`.

Edite o arquivo `configuracoes.json` e insira suas credenciais e configurações personalizadas para o banco de dados, servidor de e-mail e tickers de ações.

## Como Usar

1. Verifique se o banco de dados está rodando e acessível com as credenciais fornecidas no arquivo configuracoes.json.

2. Execute o script para consultar cotações e armazená-las no banco de dados:

    ```bash
    python consultar_cotacao.py
    ```

3. O script irá consultar as cotações a cada intervalo configurado (por padrão, a cada 5 minutos). Quando o preço de uma ação atingir o valor definido em preco_alerta, um e-mail será enviado.

## Contribuição

Contribuições são bem-vindas!

## Autor

- [Luiz Elias](https://github.com/luizelias8)