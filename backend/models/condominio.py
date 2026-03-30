from ..extensions import db
from ..utils.datetime_utils import get_current_time


class Condominio(db.Model):
    __tablename__ = 'condominio'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=get_current_time)

    solicitacoes = db.relationship('Solicitacao', backref='condominio_ref', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "is_active": self.is_active,
            "data_criacao": self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None,
        }