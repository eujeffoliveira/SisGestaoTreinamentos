from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'TBROLE'
    
    ID_ROLE = db.Column(db.Integer, primary_key=True)
    NOME_ROLE = db.Column(db.String(50), nullable=False)
    DESCRICAO = db.Column(db.String(255))
    DATA_CADASTRO = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuarios = db.relationship('User', backref='role', lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'TBUSUARIO'
    
    ID_USUARIO = db.Column(db.Integer, primary_key=True)
    NOME_USUARIO = db.Column(db.String(50), nullable=False)
    LOGIN = db.Column(db.String(50), nullable=False, unique=True)
    SENHA = db.Column(db.String(50), nullable=False)
    EMAIL = db.Column(db.String(50), nullable=False, unique=True)
    ID_ROLE = db.Column(db.Integer, db.ForeignKey('TBROLE.ID_ROLE'), nullable=False)
    ATIVO = db.Column(db.Boolean, nullable=False, default=True)
    DATA_CADASTRO = db.Column(db.DateTime, default=datetime.utcnow)
    ULTIMO_ACESSO = db.Column(db.DateTime)

    def get_id(self):
        return str(self.ID_USUARIO)

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
