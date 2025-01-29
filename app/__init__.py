from flask import Flask, render_template
from app.extensions import db
from app.config import Config

def create_app():
    
    # Cria a instância da aplicação Flask
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configurações da aplicação (como banco de dados, chave secreta, etc.)
    app.config.from_object(Config)
    
    # Inicializa o SQLAlchemy com a aplicação
    db.init_app(app)
    
    # Rota para a página inicial
    @app.route('/')
    def home():
        return render_template('home/Index.html')

    # Registra os blueprints (módulos)
    from app.cargo import bp as cargo_bp
    app.register_blueprint(cargo_bp, url_prefix='/cargos')
    
    # Registra os blueprints (erros)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app
