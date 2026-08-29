from functools import wraps

import jwt
from flask import current_app, jsonify, request

from ..models import Usuario


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token ausente"}), 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Formato do token inválido"}), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            usuario = Usuario.query.get(payload["usuario_id"])

            if not usuario:
                return jsonify({"error": "Usuário não encontrado"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated