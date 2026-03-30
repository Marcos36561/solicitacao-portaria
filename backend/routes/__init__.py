from .condominios import condominios_bp
from .solicitacoes import solicitacoes_bp
from .uploads import uploads_bp


def register_blueprints(app):
    app.register_blueprint(condominios_bp)
    app.register_blueprint(solicitacoes_bp)
    app.register_blueprint(uploads_bp)