from flask import render_template, request, jsonify, Response, send_file
from flask_login import login_required
from app.extensions import db
from app.logs import bp
from app.logs.models import Log
from app.autenticacao.models import User
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
import json
import pandas as pd

@bp.route('/logs', methods=['GET'])
@login_required
def listar_logs():
    """
    Exibe a página de logs com filtros opcionais.
    Permite filtrar por usuário, ação realizada, e intervalo de datas.
    """

    # Obtendo parâmetros de filtragem da requisição
    usuario_id = request.args.get('usuario_id')
    acao = request.args.get('acao')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # Construindo a query base
    query = db.session.query(Log)

    # Aplicando filtros conforme os parâmetros fornecidos
    if usuario_id:
        try:
            usuario_id = int(usuario_id)  # Converte para inteiro para evitar erros de comparação
            query = query.filter(Log.ID_USUARIO == usuario_id)
        except ValueError:
            return jsonify({"erro": "ID de usuário inválido"}), 400

    if acao:
        query = query.filter(Log.ACAO.ilike(f"%{acao}%"))  # Permite buscas parciais

    # Tratamento e conversão das datas
    formato_data = "%Y-%m-%d"
    try:
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, formato_data)
            query = query.filter(Log.DATA_HORA >= data_inicio)

        if data_fim:
            data_fim = datetime.strptime(data_fim, formato_data)
            data_fim = datetime.combine(data_fim, datetime.max.time())  # Final do dia
            query = query.filter(Log.DATA_HORA <= data_fim)
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD."}), 400

    # Obtém os logs filtrados, ordenados pela data mais recente primeiro
    logs = query.order_by(Log.DATA_HORA.desc()).all()
    usuarios = User.query.all()  # Obtém a lista de usuários para exibição no filtro

    return render_template('logs/index.html', logs=logs, usuarios=usuarios)


@bp.route('/detalhes/<int:id>', methods=['GET'])
@login_required
def detalhes_log(id):
    """
    Retorna os detalhes do log no formato JSON para exibição no modal.
    """

    log = Log.query.get_or_404(id)  # Busca o log pelo ID ou retorna erro 404 se não encontrado
    
    # Converte JSON armazenado como string para um dicionário Python
    dados_anteriores = log.DADOS_ANTERIORES
    dados_novos = log.DADOS_NOVOS
    
    try:
        dados_anteriores = json.loads(log.DADOS_ANTERIORES) if log.DADOS_ANTERIORES else {}
    except json.JSONDecodeError:
        pass  # Mantém como está caso não seja um JSON válido

    try:
        dados_novos = json.loads(log.DADOS_NOVOS) if log.DADOS_NOVOS else {}
    except json.JSONDecodeError:
        pass  # Mantém como está caso não seja um JSON válido

    dados = {
        "ID_LOG": log.ID_LOG,
        "USUARIO": log.usuario.NOME_USUARIO,
        "ACAO": log.ACAO,
        "TABELA": log.TABELA,
        "ID_REGISTRO": log.ID_REGISTRO,
        "DADOS_ANTERIORES": json.dumps(dados_anteriores, indent=4, ensure_ascii=False),  # Enviar como JSON formatado
        "DADOS_NOVOS": json.dumps(dados_novos, indent=4, ensure_ascii=False),
        "DATA_HORA": log.DATA_HORA.strftime('%d/%m/%Y %H:%M:%S')
    }

    return jsonify(dados)


def registrar_log(usuario_id, acao, tabela, id_registro, dados_anteriores=None, dados_novos=None):
    """
    Registra uma ação no log do sistema.
    
    Parâmetros:
        usuario_id (int): ID do usuário que realizou a ação.
        acao (str): Tipo da ação realizada (INSERT, UPDATE, DELETE).
        tabela (str): Nome da tabela onde a ação ocorreu.
        id_registro (int): ID do registro afetado.
        dados_anteriores (dict, opcional): Estado anterior dos dados, se aplicável.
        dados_novos (dict, opcional): Estado atual dos dados, se aplicável.
    """

    # Converte os dados anteriores e novos para JSON se não forem nulos
    dados_anteriores_json = json.dumps(dados_anteriores, ensure_ascii=False) if dados_anteriores else None
    dados_novos_json = json.dumps(dados_novos, ensure_ascii=False) if dados_novos else None

    # Cria o objeto de log
    novo_log = Log(
        ID_USUARIO=usuario_id,
        ACAO=acao,
        TABELA=tabela,
        ID_REGISTRO=id_registro,
        DADOS_ANTERIORES=dados_anteriores_json,
        DADOS_NOVOS=dados_novos_json,
        DATA_HORA=datetime.now()
    )

    # Adiciona e persiste o log no banco de dados
    db.session.add(novo_log)
    db.session.commit()
    

# Rota para exportar os dados do log em formato CSV, Excel ou PDF
@bp.route('/exportar/<formato>', methods=['GET'])
@login_required
def exportar_logs(formato):
    """ Exporta os logs nos formatos CSV, Excel ou PDF """
    
    logs = Log.query.order_by(Log.DATA_HORA.desc()).all()  # Obtém todos os logs ordenados

    # Converte os dados para um formato estruturado
    data = []
    for log in logs:
        data.append({
            "ID_LOG": log.ID_LOG,
            "USUARIO": log.usuario.NOME_USUARIO,
            "ACAO": log.ACAO,
            "TABELA": log.TABELA,
            "ID_REGISTRO": log.ID_REGISTRO,
            "DADOS_ANTERIORES": json.loads(log.DADOS_ANTERIORES) if log.DADOS_ANTERIORES else None,
            "DADOS_NOVOS": json.loads(log.DADOS_NOVOS) if log.DADOS_NOVOS else None,
            "DATA_HORA": log.DATA_HORA.strftime('%d/%m/%Y %H:%M:%S')
        })

    df = pd.DataFrame(data)  # Converte para DataFrame

    # Exportação para CSV
    if formato == 'csv':
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8')
        return Response(csv_data, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=logs.csv"})

    # Exportação para Excel
    elif formato == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Logs")
        output.seek(0)
        return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         as_attachment=True, download_name="logs.xlsx")

    return jsonify({"erro": "Formato não suportado"}), 400
