from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'TBROLE'
    
    ID_ROLE = db.Column(db.Integer, primary_key=True)  # Identificador único do perfil
    NOME_ROLE = db.Column(db.String(50), nullable=False)  # Nome do perfil
    DESCRICAO = db.Column(db.String(255))  # Descrição do perfil
    DATA_CADASTRO = db.Column(db.DateTime, default=datetime.utcnow)  # Data de cadastro do perfil
    
    usuarios = db.relationship('User', backref='role', lazy=True)  # Relacionamento com usuários

class User(db.Model, UserMixin):
    __tablename__ = 'TBUSUARIO'
    
    ID_USUARIO = db.Column(db.Integer, primary_key=True)  # Identificador único do usuário
    NOME_USUARIO = db.Column(db.String(50), nullable=False)  # Nome do usuário
    LOGIN = db.Column(db.String(50), nullable=False, unique=True)  # Login do usuário (único)
    SENHA = db.Column(db.String(100), nullable=False)  # Senha do usuário (aumentado para 100 caracteres para hash)
    EMAIL = db.Column(db.String(50), nullable=False, unique=True)  # Email do usuário (único)
    ID_ROLE = db.Column(db.Integer, db.ForeignKey('TBROLE.ID_ROLE'), nullable=False)  # ID do perfil do usuário
    ATIVO = db.Column(db.Boolean, nullable=False, default=True)  # Status do usuário (ativo/inativo)
    DATA_CADASTRO = db.Column(db.DateTime, default=datetime.utcnow)  # Data de cadastro do usuário
    ULTIMO_ACESSO = db.Column(db.DateTime)  # Data do último acesso do usuário

    def get_id(self):
        return str(self.ID_USUARIO)  # Retorna o ID do usuário como string

    def to_dict(self):
        return {
            'ID_USUARIO': self.ID_USUARIO,
            'NOME_USUARIO': self.NOME_USUARIO,
            'LOGIN': self.LOGIN,
            'EMAIL': self.EMAIL,
            'ID_ROLE': self.ID_ROLE,
            'ATIVO': self.ATIVO,
            'DATA_CADASTRO': self.DATA_CADASTRO.isoformat() if self.DATA_CADASTRO else None,
            'ULTIMO_ACESSO': self.ULTIMO_ACESSO.isoformat() if self.ULTIMO_ACESSO else None
        }
