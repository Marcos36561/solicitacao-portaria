from flask import Blueprint, current_app, jsonify, request
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Usuario

auth_bp = Blueprint('auth', __name__)


def gerar_token(usuario):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({"usuario_id": usuario.id, "email": usuario.email})


@auth_bp.route('/auth/cadastro', methods=['POST'])
def cadastrar_usuario():
    try:
        data = request.get_json() or {}

        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')

        if not nome or not email or not senha:
            return jsonify({"error": "Campos obrigatórios ausentes: nome, email e senha"}), 400

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return jsonify({"error": "Já existe um usuário com este email"}), 400

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            is_admin=data.get('is_admin', False)
        )

        db.session.add(usuario)
        db.session.commit()

        return jsonify(usuario.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao cadastrar usuário", "message": str(e)}), 500


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}

        email = data.get('email')
        senha = data.get('senha')

        if not email or not senha:
            return jsonify({"error": "Campos obrigatórios ausentes: email e senha"}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not check_password_hash(usuario.senha_hash, senha):
            return jsonify({"error": "Email ou senha inválidos"}), 401

        return jsonify({
            "token": gerar_token(usuario),
            "usuario": usuario.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": "Erro ao fazer login", "message": str(e)}), 500
