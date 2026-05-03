from ..extensions import db
from ..utils.datetime_utils import get_current_time


class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=get_current_time)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "is_admin": self.is_admin,
            "data_criacao": self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None,
        }