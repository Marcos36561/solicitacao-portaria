from flask import Blueprint, request, jsonify

from ..extensions import db
from ..models import Solicitacao, Condominio
from ..utils.datetime_utils import parse_datetime

solicitacoes_bp = Blueprint('solicitacoes', __name__)


@solicitacoes_bp.route('/solicitacoes', methods=['POST'])
def cadastrar_solicitacao():
    try:
        data = request.get_json()

        if not data.get('nome') or not data.get('tipo'):
            return jsonify({"error": "Campos obrigatórios ausentes: nome e tipo"}), 400

        data_visita = None
        data_expiracao = None

        if data.get('data_visita'):
            try:
                data_visita = parse_datetime(data['data_visita'])
            except ValueError as e:
                return jsonify({
                    "error": "Erro na conversão de data_visita",
                    "detalhes": str(e),
                    "formato_esperado": "YYYY-MM-DD HH:MM:SS"
                }), 400

        if data.get('data_expiracao'):
            try:
                data_expiracao = parse_datetime(data['data_expiracao'])
            except ValueError as e:
                return jsonify({
                    "error": "Erro na conversão de data_expiracao",
                    "detalhes": str(e),
                    "formato_esperado": "YYYY-MM-DD HH:MM:SS"
                }), 400

        status_valido = ["pendente", "confirmado", "cancelado"]
        if data.get('status') not in status_valido:
            return jsonify({"error": f"Status inválido. Escolha entre {status_valido}"}), 400

        nova_solicitacao = Solicitacao(
            nome=data['nome'],
            tipo=data['tipo'],
            condominio_id=data.get('condominio_id'),
            condominio=data.get('condominio'),
            data_visita=data_visita,
            data_expiracao=data_expiracao,
            placa_veiculo=data.get('placa_veiculo'),
            observacoes=data.get('observacoes'),
            imagem_url=data.get('imagem_url'),
            documento_url=data.get('documento_url'),
            status=data.get('status', 'pendente')
        )

        db.session.add(nova_solicitacao)
        db.session.commit()

        return jsonify(nova_solicitacao.to_dict()), 201

    except Exception as e:
        return jsonify({"error": "Erro ao criar solicitação", "message": str(e)}), 500


@solicitacoes_bp.route('/solicitacoes', methods=['GET'])
def listar_solicitacoes():
    try:
        solicitacoes = Solicitacao.query.filter_by(is_deleted=False).all()

        if not solicitacoes:
            return jsonify({"message": "Nenhuma solicitação encontrada"}), 404

        return jsonify([s.to_dict() for s in solicitacoes]), 200

    except Exception as e:
        return jsonify({"error": "Erro ao listar solicitações", "message": str(e)}), 500


@solicitacoes_bp.route('/solicitacoes/<int:id>', methods=['GET'])
def obter_solicitacao(id):
    solicitacao = Solicitacao.query.get(id)
    if not solicitacao or solicitacao.is_deleted:
        return jsonify({"error": "Solicitação não encontrada"}), 404
    return jsonify(solicitacao.to_dict())


@solicitacoes_bp.route('/solicitacoes/<int:id>', methods=['PUT'])
def atualizar_solicitacao(id):
    try:
        data = request.get_json()

        solicitacao = Solicitacao.query.get(id)
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404

        solicitacao.nome = data.get('nome', solicitacao.nome)
        solicitacao.tipo = data.get('tipo', solicitacao.tipo)

        if 'condominio_id' in data:
            solicitacao.condominio_id = data['condominio_id']
            if data['condominio_id']:
                condominio = Condominio.query.get(data['condominio_id'])
                if condominio:
                    solicitacao.condominio = condominio.nome
        elif 'condominio' in data:
            solicitacao.condominio = data['condominio']

        solicitacao.placa_veiculo = data.get('placa_veiculo', solicitacao.placa_veiculo)
        solicitacao.observacoes = data.get('observacoes', solicitacao.observacoes)

        if 'imagem_url' in data:
            solicitacao.imagem_url = data['imagem_url']

        if 'documento_url' in data:
            solicitacao.documento_url = data['documento_url']

        if 'data_visita' in data:
            if data['data_visita'] is None or data['data_visita'] == '':
                solicitacao.data_visita = None
            else:
                try:
                    solicitacao.data_visita = parse_datetime(data['data_visita'])
                except ValueError as e:
                    return jsonify({
                        "error": "Erro na conversão de data_visita",
                        "detalhes": str(e),
                        "formato_esperado": "YYYY-MM-DD HH:MM:SS"
                    }), 400

        if 'data_expiracao' in data:
            if data['data_expiracao'] is None or data['data_expiracao'] == '':
                solicitacao.data_expiracao = None
            else:
                try:
                    solicitacao.data_expiracao = parse_datetime(data['data_expiracao'])
                except ValueError as e:
                    return jsonify({
                        "error": "Erro na conversão de data_expiracao",
                        "detalhes": str(e),
                        "formato_esperado": "YYYY-MM-DD HH:MM:SS"
                    }), 400

        if 'status' in data:
            status_valido = ["pendente", "confirmado", "cancelado"]
            if data['status'] not in status_valido:
                return jsonify({"error": f"Status inválido. Escolha entre {status_valido}"}), 400
            solicitacao.status = data['status']

        db.session.commit()

        return jsonify(solicitacao.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "Erro ao atualizar solicitação", "message": str(e)}), 500


@solicitacoes_bp.route('/solicitacoes/<int:id>', methods=['DELETE'])
def deletar_solicitacao(id):
    try:
        solicitacao = Solicitacao.query.get(id)
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404

        solicitacao.is_deleted = True
        db.session.commit()

        return jsonify({"message": "Solicitação deletada com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao deletar solicitação", "message": str(e)}), 500