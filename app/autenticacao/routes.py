from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app.extensions import db, bcrypt
from app.autenticacao import bp
from app.autenticacao.models import User, Role
from app.logs.routes import registrar_log

# ========================================================
#               ROTAS DE AUTENTICAÇÃO
# ========================================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Manipula o login de usuários.
    Se o usuário já estiver autenticado, redireciona para a home.
    Caso contrário, processa o formulário de login e verifica as credenciais.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redireciona se já estiver autenticado

    if request.method == 'POST':
        # Processa os dados do formulário de login
        login_input = request.form['login']
        senha = request.form['senha']

        # Busca um usuário ativo com o login informado
        user = User.query.filter_by(LOGIN=login_input, ATIVO=True).first()

        if user and bcrypt.check_password_hash(user.SENHA, senha):
            # Credenciais corretas: realiza o login
            login_user(user)
            # Atualiza o registro do último acesso do usuário
            user.ULTIMO_ACESSO = datetime.utcnow()
            db.session.commit()

            # Redireciona para a página de destino (se houver) ou para a home
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash('Login ou senha inválidos', 'danger')  # Mensagem de erro

    # Renderiza o template de login
    return render_template('autenticacao/login.html')


@bp.route('/logout')
@login_required
def logout():
    """
    Realiza o logout do usuário.
    Após o logout, exibe uma mensagem de sucesso e redireciona para a página de login.
    """
    logout_user()
    flash('Você foi desconectado com sucesso', 'success')
    return redirect(url_for('auth.login'))


# ========================================================
#             ROTAS DE REGISTRO DE USUÁRIOS
# ========================================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Cadastra novos usuários no sistema.
    Valida se o login e o email já estão em uso e, em caso de sucesso, registra o usuário.
    """
    if request.method == 'POST':
        # Obtém os dados do formulário de registro
        nome = request.form['nome']
        login_input = request.form['login']
        email = request.form['email']
        senha = request.form['senha']
        id_role = request.form['id_role']  # ID do perfil selecionado

        # Verifica se o login já existe
        if User.query.filter_by(LOGIN=login_input).first():
            flash('Este login já está em uso', 'danger')
            return redirect(url_for('auth.register'))

        # Verifica se o email já existe
        if User.query.filter_by(EMAIL=email).first():
            flash('Este email já está em uso', 'danger')
            return redirect(url_for('auth.register'))

        # Gera o hash da senha
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Cria o objeto do novo usuário
        novo_usuario = User(
            NOME_USUARIO=nome,
            LOGIN=login_input,
            EMAIL=email,
            SENHA=senha_hash,
            ID_ROLE=id_role,
            ATIVO=True
        )

        try:
            # Adiciona o novo usuário à sessão e salva no banco de dados
            db.session.add(novo_usuario)
            db.session.commit()

            # Registra a ação no log
            registrar_log(
                usuario_id=current_user.ID_USUARIO if current_user.is_authenticated else None,
                acao='INSERT',
                tabela='TBUSUARIO',
                id_registro=novo_usuario.ID_USUARIO,
                dados_novos=novo_usuario.to_dict()
            )

            flash('Usuário registrado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Em caso de erro, reverte a operação e exibe uma mensagem
            db.session.rollback()
            flash('Erro ao registrar usuário. Por favor, tente novamente.', 'danger')
            print(f"Erro no registro: {str(e)}")  # Para debug

    # Renderiza o template de registro
    return render_template('autenticacao/register.html')


# ========================================================
#       ROTAS DE GERENCIAMENTO DE ACESSO (ADMIN)
# ========================================================

@bp.route('/gerenciar-acesso')
@login_required
def gerenciar_acesso():
    """
    Interface de gerenciamento de usuários e perfis.
    Apenas usuários com perfil de 'Administrador' podem acessar esta rota.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('home'))

    # Renderiza a interface passando a lista de usuários e perfis
    return render_template(
        'autenticacao/gerenciar_acesso.html',
        usuarios=User.query.all(),
        roles=Role.query.all()
    )


# ========================================================
#        API - GERENCIAMENTO DE USUÁRIOS (ADMIN)
# ========================================================

@bp.route('/usuario/<int:id>', methods=['GET'])
@login_required
def get_usuario(id):
    """
    Retorna os dados de um usuário específico no formato JSON.
    Requer que o usuário atual seja Administrador.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    usuario = User.query.get_or_404(id)
    return jsonify(usuario.to_dict())


@bp.route('/usuario/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_usuario(id):
    """
    Ativa ou desativa um usuário.
    Requer que o usuário atual seja Administrador.
    Recebe via JSON o novo status (ativo/inativo) e registra a alteração.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    usuario = User.query.get_or_404(id)
    data = request.get_json()

    try:
        # Armazena os dados anteriores para o log
        dados_anteriores = usuario.to_dict()

        # Atualiza o status do usuário conforme o dado recebido
        usuario.ATIVO = data['ativo']
        db.session.commit()

        # Registra a alteração no log
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='UPDATE',
            tabela='TBUSUARIO',
            id_registro=usuario.ID_USUARIO,
            dados_anteriores=dados_anteriores,
            dados_novos=usuario.to_dict()
        )

        return jsonify({'message': 'Status do usuário atualizado'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/usuario/<int:id>', methods=['PUT'])
@login_required
def update_usuario(id):
    """
    Atualiza os dados de um usuário.
    Requer que o usuário atual seja Administrador.
    Permite atualizar nome, email, perfil e, opcionalmente, a senha.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    usuario = User.query.get_or_404(id)
    data = request.get_json()

    try:
        # Guarda os dados anteriores para o log
        dados_anteriores = usuario.to_dict()

        # Atualiza os campos do usuário com os dados recebidos
        usuario.NOME_USUARIO = data['nome']
        usuario.EMAIL = data['email']
        usuario.ID_ROLE = data['id_role']

        # Se uma nova senha foi informada, atualiza a senha
        if 'senha' in data and data['senha']:
            usuario.SENHA = bcrypt.generate_password_hash(data['senha']).decode('utf-8')

        db.session.commit()

        # Registra a alteração no log
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='UPDATE',
            tabela='TBUSUARIO',
            id_registro=usuario.ID_USUARIO,
            dados_anteriores=dados_anteriores,
            dados_novos=usuario.to_dict()
        )

        return jsonify({'message': 'Usuário atualizado com sucesso'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# Função para excluir o usuário 
@bp.route('/usuario/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_usuario(id):
    # Verifica se o usuário atual tem permissão (por exemplo, é administrador)
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    usuario = User.query.get_or_404(id)
    
    try:
        # Registra os dados anteriores para o log, se necessário
        dados_anteriores = usuario.to_dict()

        # Exclui o usuário
        db.session.delete(usuario)
        db.session.commit()

        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='DELETE',
            tabela='TBUSUARIO',
            id_registro=id,
            dados_anteriores=dados_anteriores
        )

        return jsonify({'message': 'Usuário excluído com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================================
#        API - GERENCIAMENTO DE PERFIS (ADMIN)
# ========================================================

@bp.route('/perfil', methods=['POST'])
@login_required
def add_role():
    """
    Adiciona um novo perfil (Role) ao sistema.
    Requer que o usuário atual seja Administrador.
    Recebe os dados via JSON ou via formulário e cria um novo perfil.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    # Se a requisição vier como JSON, utiliza request.get_json(), senão pega os dados do formulário.
    data = request.get_json() if request.is_json else request.form.to_dict()

    # Obtém os dados esperados
    nome_role = data.get('nome_role')
    descricao_role = data.get('descricao_role')

    # Valida os dados (você pode acrescentar outras validações, se necessário)
    if not nome_role or not descricao_role:
        return jsonify({'error': 'Nome e descrição são obrigatórios'}), 400

    try:
        # Cria um novo objeto Role com os dados recebidos
        new_role = Role(
            NOME_ROLE=nome_role,
            DESCRICAO=descricao_role
        )
        db.session.add(new_role)
        db.session.commit()

        # Registra a ação de inserção no log
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='INSERT',
            tabela='TBROLE',  # ajuste para o nome da sua tabela de perfis, se necessário
            id_registro=new_role.ID_ROLE,
            dados_novos=new_role.to_dict() if hasattr(new_role, 'to_dict') else {
                'ID_ROLE': new_role.ID_ROLE,
                'NOME_ROLE': new_role.NOME_ROLE,
                'DESCRICAO': new_role.DESCRICAO
            }
        )

        return jsonify({'message': 'Perfil criado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/perfil/<int:id>', methods=['GET'])
@login_required
def get_perfil(id):
    """
    Retorna os dados de um perfil específico (Role) no formato JSON.
    Requer que o usuário atual seja Administrador.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    role = Role.query.get_or_404(id)
    return jsonify({
        'ID_ROLE': role.ID_ROLE,
        'NOME_ROLE': role.NOME_ROLE,
        'DESCRICAO': role.DESCRICAO
    })
    
@bp.route('/perfil/<int:id>', methods=['PUT'])
@login_required
def update_perfil(id):
    """
    Atualiza os dados de um perfil.
    Requer que o usuário atual seja Administrador.
    Permite atualizar o nome e a descrição do perfil.
    """
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    # Busca o perfil ou retorna 404 se não existir
    perfil = Role.query.get_or_404(id)
    data = request.get_json()

    try:
        # Guarda os dados anteriores para o log
        dados_anteriores = perfil.to_dict() if hasattr(perfil, 'to_dict') else {
            'ID_ROLE': perfil.ID_ROLE,
            'NOME_ROLE': perfil.NOME_ROLE,
            'DESCRICAO': perfil.DESCRICAO
        }

        # Atualiza os campos do perfil com os dados recebidos
        perfil.NOME_ROLE = data.get('nome_role', perfil.NOME_ROLE)
        perfil.DESCRICAO = data.get('descricao', perfil.DESCRICAO)

        db.session.commit()

        # Registra a alteração no log
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='UPDATE',
            tabela='TBROLE',  # ajuste o nome da tabela conforme sua implementação
            id_registro=perfil.ID_ROLE,
            dados_anteriores=dados_anteriores,
            dados_novos=perfil.to_dict() if hasattr(perfil, 'to_dict') else {
                'ID_ROLE': perfil.ID_ROLE,
                'NOME_ROLE': perfil.NOME_ROLE,
                'DESCRICAO': perfil.DESCRICAO
            }
        )

        return jsonify({'message': 'Perfil atualizado com sucesso'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/perfil/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_perfil(id):
    """
    Exclui um perfil, desde que não haja nenhum usuário associado a ele.
    Requer que o usuário atual seja Administrador.
    """
    # Verifica se o usuário atual é Administrador
    if current_user.role.NOME_ROLE != 'Administrador':
        return jsonify({'error': 'Não autorizado'}), 403

    # Busca o perfil a ser excluído ou retorna 404 se não existir
    perfil = Role.query.get_or_404(id)

    # Verifica se há algum usuário associado a este perfil
    usuario_associado = User.query.filter_by(ID_ROLE=perfil.ID_ROLE).first()
    if usuario_associado:
        return jsonify({
            'error': 'Não é possível excluir o perfil, pois existem usuários associados a ele.'
        }), 400

    try:
        # Armazena os dados anteriores para registro de log
        # Caso Role possua um método to_dict(), utilize-o; senão, crie um dicionário manualmente.
        dados_anteriores = perfil.to_dict() if hasattr(perfil, 'to_dict') else {
            'ID_ROLE': perfil.ID_ROLE,
            'NOME_ROLE': perfil.NOME_ROLE,
            'DESCRICAO': perfil.DESCRICAO
        }

        # Remove o perfil e confirma a transação
        db.session.delete(perfil)
        db.session.commit()

        # Registra a ação de exclusão no log
        registrar_log(
            usuario_id=current_user.ID_USUARIO,
            acao='DELETE',
            tabela='TBROLE',  # ajuste o nome da tabela conforme sua implementação
            id_registro=id,
            dados_anteriores=dados_anteriores
        )

        return jsonify({'message': 'Perfil excluído com sucesso'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
