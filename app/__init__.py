from flask import Flask, render_template
from app.extensions import db
from app.config import Config
from flask_login import LoginManager, login_required
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
bycrypt = Bcrypt()

def create_app():
    
    # Cria a instância da aplicação Flask
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configurações do LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Define a view de login
    login_manager.login_message = 'Por favor, faça login para acessar o sistema.'
    login_manager.login_message_category = 'info'
    
    # rotrar para a página de login
    @login_manager.user_loader
    def load_user(user_id):
        from app.autenticacao.models import User
        return User.query.get(int(user_id))
    
    # Configurações da aplicação (como banco de dados, chave secreta, etc.)
    app.config.from_object(Config)
    
    # Inicializa o SQLAlchemy com a aplicação
    db.init_app(app)
    
    # Rota para a página de login
    @app.route('/login')
    def login():
        return render_template('autenticacao/login.html')
    
    # Rota para a página inicial
    @app.route('/')
    @login_required
    def home():
        return render_template('home/Index.html')
    
    # Registra os blueprints (autenticação)
    from app.autenticacao import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Registra os blueprints (módulos)
    from app.cargo import bp as cargo_bp
    app.register_blueprint(cargo_bp, url_prefix='/cargos')
    
    # Registra os blueprints (erros)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app
