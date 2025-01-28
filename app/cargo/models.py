from app.extensions import db

class Cargo(db.Model):
    __tablename__ = 'TBCARGO'
    ID_CARGO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NOME_CARGO = db.Column(db.String(100), nullable=False)
    DESCRICAO = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Cargo {self.NOME_CARGO}>'
