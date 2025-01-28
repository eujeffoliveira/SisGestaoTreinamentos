from flask import Flask
from app.config import Config

def create_app():
    # Cria a instância da aplicação Flask
    app = Flask(__name__)
    
    # Configurações da aplicação (como banco de dados, chave secreta, etc.)
    app.config.from_object(Config)

    # Registra os blueprints (módulos)
    from app.cargo import bp as cargo_bp
    app.register_blueprint(cargo_bp, url_prefix='/cargos')

    return app
