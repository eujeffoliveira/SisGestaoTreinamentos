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
    query = Log.query

    # Aplicando filtros conforme os parâmetros fornecidos
    if usuario_id:
        query = query.filter(Log.ID_USUARIO == usuario_id)
    if acao:
        query = query.filter(Log.ACAO == acao)

    # Tratamento e conversão das datas
    formato_data = "%Y-%m-%d"  # Define o formato esperado para as datas
    try:
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, formato_data)
            query = query.filter(Log.DATA_HORA >= data_inicio)
        if data_fim:
            data_fim = datetime.strptime(data_fim, formato_data)
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
    
    # Converte JSON armazenado como string para um dicionário python
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
        DATA_HORA=datetime.timezone.UTC()
    )

    # Adiciona e persiste o log no banco de dados
    db.session.add(novo_log)
    db.session.commit()

# Rota para exportar os dados do log em formato CSV, Excel ou PDF
@bp.route('/exportar/<formato>', methods=['GET'])
@login_required
def exportar_logs(formato):
    """ Exporta os logs nos formatos CSV, Excel ou PDF """
    
    logs = Log.query.all()  # Obtém todos os logs do banco

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

    # Exportação para PDF
    if formato == 'pdf':
        output = BytesIO()
        p = canvas.Canvas(output, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 50, "Relatório de Logs")

        y = height - 70
        for log in data:
            p.setFont("Helvetica", 10)
            linha_principal = f"{log['DATA_HORA']} - {log['USUARIO']} - {log['ACAO']} - {log['TABELA']} (ID: {log['ID_REGISTRO']})"
            p.drawString(50, y, linha_principal)
            y -= 15

            # Dados Anteriores
            if log['DADOS_ANTERIORES'] and log['DADOS_ANTERIORES'] != "-":
                p.setFont("Helvetica-Bold", 9)
                p.drawString(70, y, "Dados Anteriores:")
                y -= 12
                p.setFont("Helvetica", 8)

                # Converte dicionário para string formatada
                dados_anteriores = str(log['DADOS_ANTERIORES'])
                wrapped_text = simpleSplit(dados_anteriores, "Helvetica", 8, width - 100)
                for line in wrapped_text:
                    p.drawString(90, y, line)
                    y -= 10

            # Dados Novos
            if log['DADOS_NOVOS'] and log['DADOS_NOVOS'] != "-":
                p.setFont("Helvetica-Bold", 9)
                p.drawString(70, y, "Dados Novos:")
                y -= 12
                p.setFont("Helvetica", 8)

                # Converte dicionário para string formatada
                dados_novos = str(log['DADOS_NOVOS'])
                wrapped_text = simpleSplit(dados_novos, "Helvetica", 8, width - 100)
                for line in wrapped_text:
                    p.drawString(90, y, line)
                    y -= 10

            # Linha separadora
            p.line(50, y, width - 50, y)
            y -= 15

            # Verifica se precisa de nova página
            if y < 50:
                p.showPage()
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, height - 50, "Relatório de Logs (Continuação)")
                y = height - 70

        p.save()
        output.seek(0)
        return send_file(output, 
                        mimetype="application/pdf",
                        as_attachment=True, 
                        download_name="logs.pdf")


    return jsonify({"erro": "Formato não suportado"}), 400