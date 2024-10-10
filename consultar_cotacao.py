import os
import sys
import json
from pprint import pprint
import yfinance as yf
import psycopg2
import schedule
import time
import smtplib
from email.mime.text import MIMEText

# Define o diretório do app verificando se o script está rodando em uma versão "congelada".
diretorio_app = os.path.dirname(sys.executable if hasattr(sys, 'frozen') else __file__)

def carregar_configuracoes():
    """Carrega as configurações do arquivo JSON."""
    with open(os.path.join(diretorio_app, 'configuracoes.json'), 'r') as arquivo:
        return json.load(arquivo)

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL e retorna a conexão."""
    # Carrega as configurações da seção DATABASE do arquivo JSON
    configuracoes = carregar_configuracoes()
    configuracoes_banco_dados = configuracoes['banco_dados']

    try:
        conexao = psycopg2.connect(
            dbname=configuracoes_banco_dados['nome'],
            user=configuracoes_banco_dados['usuario'],
            password=configuracoes_banco_dados['senha'],
            host=configuracoes_banco_dados['servidor'],
            port=configuracoes_banco_dados['porta']
        )
        return conexao
    except Exception as e:
        print(f'Erro ao conectar ao banco de dados: {e}')
        return None

def criar_tabela_cotacoes():
    """Cria a tabela de cotações caso não exista."""
    # Chama a função conectar_banco para obter a conexão
    conexao = conectar_banco()

    if conexao is None:
        print('Não foi possível estabelecer conexão com o banco de dados.')
        return

    cursor = conexao.cursor() # Obtendo o cursor da conexão
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cotacoes (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                cotacao_atual NUMERIC NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conexao.commit() # Comitando a criação da tabela
        print(f"Tabela 'cotacoes' criada ou já existente.")
    except Exception as e:
        print(f'Erro ao criar a tabela: {e}')
        conexao.rollback() # Reverter em caso de erro
    finally:
        cursor.close() # Fechando o cursor
        conexao.close() # Fechando a conexão

def armazenar_cotacao(ticker, cotacao_atual):
    """Armazena a cotação atual no banco de dados."""
    # Chama a função conectar_banco para obter a conexão
    conexao = conectar_banco()

    if conexao is None:
        print('Não foi possível estabelecer conexão com o banco de dados.')
        return

    cursor = conexao.cursor() # Obtendo o cursor da conexão
    try:
        # Inserindo os dados na tabela cotacoes
        cursor.execute("""
            INSERT INTO cotacoes (ticker, cotacao_atual)
            VALUES (%s, %s);
        """, (ticker, cotacao_atual))
        conexao.commit() # Comitando a inserção dos dados
        print(f'Cotação de {ticker} armazenada com sucesso.')
    except Exception as e:
        print(f'Erro ao armazenar a cotação: {e}')
        conexao.rollback() # Reverter em caso de erro
    finally:
        cursor.close() # Fechando o cursor
        conexao.close() # Fechando a conexão

def enviar_email(ticker, cotacao_atual):
    """Envia um e-mail com o alerta da cotação."""
    configuracoes = carregar_configuracoes()
    configuracoes_email = configuracoes['email']

    try:
        servidor_smtp = configuracoes_email['servidor_smtp']
        porta_smtp = configuracoes_email['porta_smtp']
        usuario = configuracoes_email['usuario']
        senha = configuracoes_email['senha']
        destinatario = configuracoes_email['destinatario']

        # Criando o corpo do e-mail
        mensagem = f'A cotação da ação {ticker} atingiu R$ {cotacao_atual:.2f}, abaixo do seu limite definido.'
        msg = MIMEText(mensagem)
        msg['Subject'] = f'Alerta de cotação: {ticker}'
        msg['From'] = usuario
        msg['To'] = destinatario

        # Enviando o e-mail
        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls() # Usando TLS
            servidor.login(usuario, senha)
            servidor.sendmail(usuario, destinatario, msg.as_string())
            print(f'E-mail de alerta enviado para {destinatario} sobre {ticker}.')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {e}')

def consultar_cotacoes():
    """Consulta as cotações atuais para uma lista de tickers e armazena no banco de dados."""
    # Carregar configurações do arquivo JSON
    configuracoes = carregar_configuracoes()
    tickers = configuracoes['tickers']

    # Itera sobre a lista de tickers e verifica a cotação atual para cada um
    for ticker_obj in tickers:
        ticker = ticker_obj['ticker'] + '.SA' # Adiciona o sufixo .SA
        preco_alerta = ticker_obj['preco_alerta']

        # Tenta obter a cotação atual da ação e armazenar no banco de dados
        try:
            acao = yf.Ticker(ticker)
            informacoes = acao.info
            cotacao_atual = informacoes.get('currentPrice', 'Cotação não disponível')

            # Armazenar a cotação apenas se estiver disponível
            if cotacao_atual != 'Cotação não disponível':
                armazenar_cotacao(ticker, cotacao_atual)
                print(f'Cotação de {ticker}: {cotacao_atual}')

                # Verificar se a cotação atingiu o valor de alerta
                if cotacao_atual <= preco_alerta:
                    enviar_email(ticker, cotacao_atual)
            else:
                print(f'Não foi possível obter a cotação para {ticker}')

        except Exception as e:
            print(f'Erro ao consultar {ticker}: {e}')

def agendar_consulta():
    """Agenda a consulta de cotações."""
    # Carrega as configurações do arquivo JSON
    configuracoes = carregar_configuracoes()
    configuracoes_agendamento = configuracoes['agendamento']

    # Obtém o intervalo de minutos da seção agendamento
    intervalo_minutos = configuracoes_agendamento['intervalo_minutos']

    # Agendando a consulta para ocorrer a cada X minutos, conforme definido nas configurações
    schedule.every(intervalo_minutos).minutes.do(consultar_cotacoes)

    print(f"Consulta de cotações agendada para ocorrer a cada {intervalo_minutos} minutos.")

    # Loop infinito para manter o agendamento funcionando
    while True:
        schedule.run_pending() # Executa as tarefas agendadas que estão pendentes
        time.sleep(1) # Aguarda 1 segundo antes de verificar novamente

if __name__ == '__main__':
    # Consultar as cotações pela primeira vez
    consultar_cotacoes()
    # Iniciar o agendamento
    agendar_consulta()