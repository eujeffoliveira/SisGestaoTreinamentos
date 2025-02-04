import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') # Chave secreta para proteção contra CSRF
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') # URL de conexão com o banco de dados
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desativa o tracking de modificações
    SESSION_COOKIE_SECURE = True # Apenas para HTTPS
    SESSION_COOKIE_HTTPONLY = True # Proteção contra ataques XSS
    SESSION_COOKIE_SAMESITE = 'Lax' # Proteção contra CSRF
    SESSION_PERMANENT = False # Sessão temporária
    BCRYPT_LOG_ROUNDS = 12 # Número de rounds para o Bcrypt