from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, bcrypt
from app.autenticacao import bp
from app.autenticacao.models import User, Role
from app.logs.routes import registrar_log
from datetime import datetime

# =========================================
# Rotas de Autenticação
# =========================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Manipula o login de usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redireciona se já estiver autenticado
        
    if request.method == 'POST':
        # Processa o formulário de login
        login = request.form['login']
        senha = request.form['senha']
        
        user = User.query.filter_by(LOGIN=login, ATIVO=True).first()  # Busca o usuário
        
        if user and bcrypt.check_password_hash(user.SENHA, senha):  # Verifica a senha
            login_user(user)  # Realiza o login
            user.ULTIMO_ACESSO = datetime.utcnow()  # Atualiza o último acesso
            db.session.commit()  # Salva as alterações no banco
            
            next_page = request.args.get('next')  # Obtém a página de redirecionamento
            return redirect(next_page if next_page else url_for('home'))  # Redireciona para a página inicial
        else:
            flash('Login ou senha inválidos', 'danger')  # Mensagem de erro
    
    return render_template('autenticacao/login.html')  # Renderiza o template de login

@bp.route('/logout')
@login_required
def logout():
    """Realiza o logout do usuário"""
    logout_user()  # Realiza o logout
    flash('Você foi desconectado com sucesso', 'success')  # Mensagem de sucesso
    return redirect(url_for('auth.login'))  # Redireciona para a página de login

# =========================================
# Rotas de Registro de Usuários
# =========================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastra novos usuários no sistema"""
    if request.method == 'POST':
        # Valida e processa o formulário de registro
        nome = request.form['nome']
        login = request.form['login']
        email = request.form['email']
        senha = request.form['senha']
        id_role = request.form['id_role']  # ID do perfil selecionado
        
        if User.query.filter_by(LOGIN=login).first():  # Verifica se o login já está em uso
            flash('Este login já está em uso', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(EMAIL=email).first():  # Verifica se o email já está em uso
            flash('Este email já está em uso', 'danger')
            return redirect(url_for('auth.register'))
        
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')  # Cria o hash da senha
        novo_usuario = User(
            NOME_USUARIO=nome,
            LOGIN=login,
            EMAIL=email,
            SENHA=senha_hash,
            ID_ROLE=id_role,
            ATIVO=True
        )
        
        try:
            db.session.add(novo_usuario)  # Adiciona novo usuário à sessão
            db.session.commit()  # Salva as alterações no banco
            
            registrar_log(
                usuario_id=current_user.ID_USUARIO if current_user.is_authenticated else None,
                acao='INSERT',
                tabela='TBUSUARIO',
                id_registro=novo_usuario.ID_USUARIO,
                dados_novos=novo_usuario.to_dict()
            )  # Registra a ação no log
            
            flash('Usuário registrado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('auth.login'))  # Redireciona para a página de login
            
        except Exception as e:
            db.session.rollback()  # Reverte as alterações em caso de erro
            flash('Erro ao registrar usuário. Por favor, tente novamente.', 'danger')  # Mensagem de erro
            print(f"Erro no registro: {str(e)}")  # Para debug
            
    return render_template('autenticacao/register.html')  # Renderiza o template de registro

# =========================================
# Rotas de Gerenciamento de Acesso (Admin)
# =========================================

@bp.route('/gerenciar-acesso')
@login_required
def gerenciar_acesso():
    """Interface de gerenciamento de usuários e perfis (requer admin)"""
    if current_user.role.NOME_ROLE != 'Administrador':
        flash('Acesso não autorizado', 'danger')  # Mensagem de acesso não autorizado
        return redirect(url_for('home'))  # Redireciona para a página inicial
    
    return render_template('autenticacao/gerenciar_acesso.html',
                         usuarios=User.query.all(),  # Obtém todos os usuários
                         roles=Role.query.all())  # Obtém todos os perfis

# =========================================
# API - Gerenciamento de Usuários (Admin)
# =========================================

@bp.route('/usuario/<int:id>', methods=['GET'])
@login_required
def get_usuario(id):
    """Obtém dados de um usuário específico (JSON)"""
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403
    
    usuario = User.query.get_or_404(id)  # Busca o usuário pelo ID ou retorna erro 404
    return jsonify(usuario.to_dict())  # Retorna os dados do usuário em formato JSON

@bp.route('/usuario/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_usuario(id):
    """Ativa/desativa um usuário (requer admin)"""
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403
    
    usuario = User.query.get_or_404(id)  # Busca o usuário pelo ID ou retorna erro 404
    data = request.get_json()  # Obtém os dados da requisição
    
    try:
        dados_anteriores = usuario.to_dict()  # Armazena os dados anteriores do usuário antes da alteração
        usuario.ATIVO = data['ativo']  # Atualiza o status do usuário (ativo/inativo)
        db.session.commit()  # Salva as alterações
        
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='UPDATE',
            tabela='TBUSUARIO',
            id_registro=usuario.ID_USUARIO,
            dados_anteriores=dados_anteriores,
            dados_novos=usuario.to_dict()
        )  # Registra a ação no log
        
        return jsonify({'message': 'Status do usuário atualizado'})  # Retorna mensagem de sucesso
        
    except Exception as e:
        db.session.rollback()  # Reverte as alterações em caso de erro
        return jsonify({'error': str(e)}), 500

@bp.route('/usuario/<int:id>', methods=['PUT'])
@login_required
def update_usuario(id):
    """Atualiza dados de um usuário (requer admin)"""
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403
    
    usuario = User.query.get_or_404(id)  # Busca o usuário pelo ID ou retorna erro 404
    data = request.get_json()  # Obtém os dados da requisição
    
    try:
        dados_anteriores = usuario.to_dict()  # Armazena os dados anteriores do usuário antes da alteração
        
        usuario.NOME_USUARIO = data['nome']   # Atualiza nome do usuário
        usuario.EMAIL = data['email']          # Atualiza email do usuário
        usuario.ID_ROLE = data['id_role']      # Atualiza perfil do usuário
        
        if 'senha' in data and data['senha']:   # Se uma nova senha for fornecida...
            usuario.SENHA = bcrypt.generate_password_hash(data['senha']).decode('utf-8')   # Atualiza a senha
            
        db.session.commit()   # Salva as alterações
        
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='UPDATE',
            tabela='TBUSUARIO',
            id_registro=usuario.ID_USUARIO,
            dados_anteriores=dados_anteriores,
            dados_novos=usuario.to_dict()
        )   # Registra a ação no log
        
        return jsonify({'message': 'Usuário atualizado com sucesso'})   # Retorna mensagem de sucesso
        
    except Exception as e:
        db.session.rollback()   # Reverte as alterações em caso de erro 
        return jsonify({'error': str(e)}), 500

# =========================================
# API - Gerenciamento de Perfis (Admin)
# =========================================

@bp.route('/perfil/<int:id>', methods=['GET'])
@login_required
def get_perfil(id):
    """Obtém dados de um perfil específico (JSON)"""
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403
    
    role = Role.query.get_or_404(id)   # Busca o perfil pelo ID ou retorna erro 404 
    return jsonify({
        'ID_ROLE': role.ID_ROLE,
        'NOME_ROLE': role.NOME_ROLE,
        'DESCRICAO': role.DESCRICAO   # Retorna os dados do perfil em formato JSON 
    })
