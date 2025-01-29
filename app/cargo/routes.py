from flask import render_template, request, redirect, url_for, flash
from app.extensions import db
from app.cargo import bp
from app.cargo.models import Cargo

# Rota para listar os cargos
@bp.route('/')
def listar_cargos():
    cargos = Cargo.query.all()
    colunas = [
        {'id': 'id', 'nome': 'ID'},
        {'id': 'nome', 'nome': 'Nome do Cargo'},
        {'id': 'descricao', 'nome': 'Descrição'}
    ]
    
    # Formata os dados para o template
    items = [{
        'id': cargo.ID_CARGO,
        'nome': cargo.NOME_CARGO,
        'descricao': cargo.DESCRICAO
    } for cargo in cargos]
    
    return render_template('cargo/index.html',
                          titulo='Cargos',
                          singular='Cargo',
                          route='cargo',
                          container_id='cargos',
                          colunas=colunas,
                          items=items)

# Rota para adicionar um cargo
@bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_cargo():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        novo_cargo = Cargo(NOME_CARGO=nome, DESCRICAO=descricao)
        db.session.add(novo_cargo)
        db.session.commit()
        flash('Cargo adicionado com sucesso!', 'success')
        return redirect(url_for('cargo.listar_cargos'))
    return render_template('cargo/create.html',  # Mudado para create.html
                          titulo='Novo Cargo',
                          route='cargo')

# Rota para editar um cargo
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_cargo(id):
    cargo = Cargo.query.get_or_404(id)
    if request.method == 'POST':
        cargo.NOME_CARGO = request.form['nome']
        cargo.DESCRICAO = request.form['descricao']
        db.session.commit()
        flash('Cargo atualizado com sucesso!', 'success')
        return redirect(url_for('cargo.listar_cargos'))
    return render_template('cargo/edit.html',  # Mudado para edit.html
                          titulo='Editar Cargo',
                          route='cargo',
                          cargo=cargo)

# Rota para excluir um cargo
@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir_cargo(id):
    cargo = Cargo.query.get_or_404(id)
    try:
        db.session.delete(cargo)
        db.session.commit()
        flash('Cargo excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir o cargo. Ele pode estar em uso.', 'error')
    return redirect(url_for('cargo.listar_cargos'))
