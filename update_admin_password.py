# update_admin_password.py
from app import create_app
from app.extensions import bcrypt, db
from app.autenticacao.models import User

app = create_app()

with app.app_context():
    # Gerar hash da senha
    senha_hash = bcrypt.generate_password_hash("admin123").decode('utf-8')
    
    # Atualizar a senha no banco
    user = User.query.filter_by(LOGIN='admin').first()
    if user:
        user.SENHA = senha_hash
        db.session.commit()
        print("Senha atualizada com sucesso!")
    else:
        print("Usuário admin não encontrado.")
