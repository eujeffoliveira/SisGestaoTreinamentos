from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, bcrypt
from app.autenticacao import bp
from app.autenticacao.models import User
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já está autenticado, redireciona para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        
        user = User.query.filter_by(LOGIN=login, ATIVO=True).first()
        
        if user and bcrypt.check_password_hash(user.SENHA, senha):
            # Login bem-sucedido
            login_user(user)
            user.ULTIMO_ACESSO = datetime.utcnow()
            db.session.commit()
            
            # Redireciona para a página que o usuário tentou acessar originalmente
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash('Login ou senha inválidos', 'danger')
    
    return render_template('autenticacao/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso', 'success')
    return redirect(url_for('auth.login'))
