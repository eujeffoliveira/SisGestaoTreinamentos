from app.logs import bp
from app.logs.models import Log
from app.extensions import db
import json

def registrar_log(usuario_id, acao, tabela, id_registro, dados_anteriores=None, dados_novos=None):
    """
    Registra uma ação no log do sistema.
    """
    log = Log(
        ID_USUARIO=usuario_id,
        ACAO=acao,
        TABELA=tabela,
        ID_REGISTRO=id_registro,
        DADOS_ANTERIORES=json.dumps(dados_anteriores) if dados_anteriores else None,
        DADOS_NOVOS=json.dumps(dados_novos) if dados_novos else None
    )
    db.session.add(log)
    db.session.commit()