from flask import Blueprint, request, jsonify

from ..extensions import db
from ..models import Condominio, Solicitacao

condominios_bp = Blueprint('condominios', __name__)


@condominios_bp.route('/condominios', methods=['GET'])
def listar_condominios():
    try:
        condominios = Condominio.query.filter_by(is_active=True).order_by(Condominio.nome).all()
        return jsonify([c.to_dict() for c in condominios]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar condomínios", "message": str(e)}), 500


@condominios_bp.route('/condominios', methods=['POST'])
def cadastrar_condominio():
    try:
        data = request.get_json()

        if not data.get('nome'):
            return jsonify({"error": "Nome do condomínio é obrigatório"}), 400

        existente = Condominio.query.filter_by(nome=data['nome']).first()
        if existente:
            return jsonify({"error": "Já existe um condomínio com este nome"}), 400

        novo = Condominio(nome=data['nome'])
        db.session.add(novo)
        db.session.commit()

        return jsonify(novo.to_dict()), 201

    except Exception as e:
        return jsonify({"error": "Erro ao criar condomínio", "message": str(e)}), 500


@condominios_bp.route('/condominios/<int:id>', methods=['GET'])
def obter_condominio(id):
    condominio = Condominio.query.get(id)
    if not condominio or not condominio.is_active:
        return jsonify({"error": "Condomínio não encontrado"}), 404
    return jsonify(condominio.to_dict())


@condominios_bp.route('/condominios/<int:id>', methods=['PUT'])
def atualizar_condominio(id):
    try:
        data = request.get_json()

        condominio = Condominio.query.get(id)
        if not condominio:
            return jsonify({"error": "Condomínio não encontrado"}), 404

        if 'nome' in data and data['nome'] != condominio.nome:
            existente = Condominio.query.filter_by(nome=data['nome']).first()
            if existente:
                return jsonify({"error": "Já existe um condomínio com este nome"}), 400

        if 'nome' in data:
            condominio.nome = data['nome']
        if 'is_active' in data:
            condominio.is_active = data['is_active']

        db.session.commit()

        return jsonify(condominio.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "Erro ao atualizar condomínio", "message": str(e)}), 500


@condominios_bp.route('/condominios/<int:id>', methods=['DELETE'])
def deletar_condominio(id):
    try:
        condominio = Condominio.query.get(id)
        if not condominio:
            return jsonify({"error": "Condomínio não encontrado"}), 404

        solicitacoes_ativas = Solicitacao.query.filter_by(
            condominio_id=id, is_deleted=False
        ).count()

        if solicitacoes_ativas > 0:
            return jsonify({
                "error": "Não é possível excluir este condomínio pois existem solicitações associadas",
                "count": solicitacoes_ativas
            }), 400

        condominio.is_active = False
        db.session.commit()

        return jsonify({"message": "Condomínio desativado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao deletar condomínio", "message": str(e)}), 500