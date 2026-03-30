from ..extensions import db
from ..utils.datetime_utils import get_current_time


class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(50))

    condominio = db.Column(db.String(100))
    condominio_id = db.Column(db.Integer, db.ForeignKey('condominio.id'))

    data_visita = db.Column(db.DateTime)
    data_expiracao = db.Column(db.DateTime)
    placa_veiculo = db.Column(db.String(20))
    observacoes = db.Column(db.Text)

    imagem_url = db.Column(db.String(255))
    documento_url = db.Column(db.String(255))

    status = db.Column(db.String(50))
    is_deleted = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=get_current_time)

    def to_dict(self):
        condominio_nome = self.condominio
        if self.condominio_ref:
            condominio_nome = self.condominio_ref.nome

        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "condominio": condominio_nome,
            "condominio_id": self.condominio_id,
            "data_visita": self.data_visita.strftime('%Y-%m-%d %H:%M:%S') if self.data_visita else None,
            "data_expiracao": self.data_expiracao.strftime('%Y-%m-%d %H:%M:%S') if self.data_expiracao else None,
            "placa_veiculo": self.placa_veiculo,
            "observacoes": self.observacoes,
            "imagem_url": self.imagem_url,
            "documento_url": self.documento_url,
            "status": self.status,
            "is_deleted": self.is_deleted,
            "data_criacao": self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None,
        }