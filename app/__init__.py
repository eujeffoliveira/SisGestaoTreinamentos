# Importações necessárias
from flask import Flask, render_template  # Flask para criar a aplicação e render_template para renderizar templates
from app.extensions import db, bcrypt  # Importa as extensões SQLAlchemy e Bcrypt
from app.config import Config  # Importa as configurações da aplicação
from flask_login import LoginManager, login_required  # Importa o gerenciador de login e o decorador de proteção de rotas

# Inicialização do gerenciador de login
# O LoginManager é responsável por gerenciar as sessões de usuário
login_manager = LoginManager()

def create_app():
    """
    Função factory que cria e configura a aplicação Flask
    Returns:
        app: A aplicação Flask configurada
    """
    # Cria a instância da aplicação Flask
    # template_folder e static_folder são definidos para apontar para os diretórios corretos
    app = Flask(__name__, 
                template_folder='../templates',  # Define o diretório de templates
                static_folder='../static')       # Define o diretório de arquivos estáticos
    
    # Carrega as configurações da aplicação do objeto Config
    # Inclui configurações como chave secreta, banco de dados, etc.
    app.config.from_object(Config)
    
    # Inicialização das extensões com a aplicação
    db.init_app(app)        # Inicializa o SQLAlchemy
    bcrypt.init_app(app)    # Inicializa o Bcrypt para hash de senhas
    login_manager.init_app(app)  # Inicializa o gerenciador de login
    
    # Configurações do gerenciador de login
    login_manager.login_view = 'auth.login'  # Define a view para login
    login_manager.login_message = 'Por favor, faça login para acessar o sistema.'  # Mensagem de redirecionamento
    login_manager.login_message_category = 'info'  # Categoria da mensagem flash
    
    # Função que carrega o usuário pelo ID
    @login_manager.user_loader
    def load_user(user_id):
        """
        Carrega um usuário pelo seu ID
        Args:
            user_id: ID do usuário a ser carregado
        Returns:
            User: Objeto do usuário ou None se não encontrado
        """
        from app.autenticacao.models import User
        return User.query.get(int(user_id))
    
    # Rota para a página inicial
    # @login_required garante que apenas usuários autenticados possam acessar
    @app.route('/')
    @login_required
    def home():
        """
        Rota da página inicial
        Returns:
            template: Renderiza o template da página inicial
        """
        return render_template('home/Index.html')
    
    # Registro dos blueprints
    # Os blueprints são usados para organizar a aplicação em módulos
    
    # Blueprint de autenticação
    from app.autenticacao import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Blueprint de logs
    from app.logs import bp as logs_bp
    app.register_blueprint(logs_bp, url_prefix='/logs')

    # Blueprint de cargos
    from app.cargo import bp as cargo_bp
    app.register_blueprint(cargo_bp, url_prefix='/cargos')
    
    # Blueprint de tratamento de erros
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Retorna a aplicação configurada
    return app
