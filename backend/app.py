import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate
from .routes import register_blueprints

# Caminho para a pasta frontend
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Garantir que pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar extensões
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Importar models para o Alembic detectar
    from . import models  # noqa: F401

    # Registrar blueprints (API)
    register_blueprints(app)

    # ===== SERVIR FRONTEND =====
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

    @app.route('/<path:filename>')
    def serve_frontend(filename):
        filepath = os.path.join(FRONTEND_FOLDER, filename)
        if os.path.isfile(filepath):
            return send_from_directory(FRONTEND_FOLDER, filename)
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

    return app