from app.extensions import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = 'TBLOG'
    
    ID_LOG = db.Column(db.Integer, primary_key=True)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('TBUSUARIO.ID_USUARIO'), nullable=False)
    ACAO = db.Column(db.String(50), nullable=False)
    TABELA = db.Column(db.String(50), nullable=False)
    ID_REGISTRO = db.Column(db.Integer, nullable=False)
    DADOS_ANTERIORES = db.Column(db.Text)
    DADOS_NOVOS = db.Column(db.Text)
    DATA_HORA = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('User', backref='logs')

# Importação no final para evitar circular import
from app.autenticacao.models import User
