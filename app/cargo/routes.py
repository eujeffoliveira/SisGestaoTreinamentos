from flask import render_template, request, redirect, url_for, flash
from app.extensions import db
from app.cargo import bp
from app.cargo.models import Cargo

# Rota para listar os cargos
@bp.route('/')
def listar_cargos():
    cargos = Cargo.query.all()  # Consulta todos os registros da tabela TBCARGO
    return render_template('cargos/cargos.html', cargos=cargos)

# Rota para adicionar um cargo
@bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_cargo():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        novo_cargo = Cargo(NOME_CARGO=nome, DESCRICAO=descricao)
        db.session.add(novo_cargo)  # Adiciona o novo cargo à sessão
        db.session.commit()  # Confirma a transação no banco de dados
        flash('Cargo adicionado com sucesso!', 'success')
        return redirect(url_for('cargo.listar_cargos'))
    return render_template('cargos/adicionar_cargo.html')

# Rota para editar um cargo
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_cargo(id):
    cargo = Cargo.query.get_or_404(id)  # Busca o cargo pelo ID ou retorna 404 se não existir
    if request.method == 'POST':
        cargo.NOME_CARGO = request.form['nome']
        cargo.DESCRICAO = request.form['descricao']
        db.session.commit()  # Atualiza o registro no banco de dados
        flash('Cargo atualizado com sucesso!', 'success')
        return redirect(url_for('cargo.listar_cargos'))
    return render_template('cargos/editar_cargo.html', cargo=cargo)

# Rota para excluir um cargo
@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir_cargo(id):
    cargo = Cargo.query.get_or_404(id)  # Busca o cargo pelo ID ou retorna 404 se não existir
    db.session.delete(cargo)  # Remove o registro do banco de dados
    db.session.commit()  # Confirma a exclusão no banco de dados
    flash('Cargo excluído com sucesso!', 'success')
    return redirect(url_for('cargo.listar_cargos'))
