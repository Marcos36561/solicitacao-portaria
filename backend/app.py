import pytz
import os
from config import config
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from pytz import timezone
from flask_migrate import Migrate
from flask import send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuração do PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://operador:operador123@localhost:5432/portaria_novo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'options': '-c timezone=America/Sao_Paulo'}}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Função para obter o horário atual em America/Sao_Paulo
def get_current_time():
    return datetime.now(timezone('America/Sao_Paulo'))

# Nova tabela de condomínios
class Condominio(db.Model):
    __tablename__ = 'condominio'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=get_current_time)
    
    # Relacionamento com a tabela de solicitações
    solicitacoes = db.relationship('Solicitacao', backref='condominio_ref', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "is_active": self.is_active,
            "data_criacao": self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None,
        }

# Modificação da tabela Solicitacao para usar a chave estrangeira
class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    
    # Campo para compatibilidade com dados legados
    condominio = db.Column(db.String(100))
    
    # Nova coluna de chave estrangeira
    condominio_id = db.Column(db.Integer, db.ForeignKey('condominio.id'))
    
    data_visita = db.Column(db.DateTime)
    data_expiracao = db.Column(db.DateTime)
    placa_veiculo = db.Column(db.String(20))
    observacoes = db.Column(db.Text)
    imagem_url = db.Column(db.String(255))
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
            "status": self.status,
            "is_deleted": self.is_deleted,
            "data_criacao": self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None,
        }


def parse_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z','+00:00')).astimezone(pytz.utc)

        saopaulo_tz = timezone('America/Sao_Paulo')

        return dt.astimezone(saopaulo_tz)
    except ValueError:
        raise ValueError(f"Formato de data inválido: {dt_str}")
    
def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rotas para gerenciar condomínios
@app.route('/condominios', methods=['GET'])
def listar_condominios():
    try:
        # Buscar todos os condomínios ativos
        condominios = Condominio.query.filter_by(is_active=True).order_by(Condominio.nome).all()
        
        return jsonify([cond.to_dict() for cond in condominios]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar condomínios", "message": str(e)}), 500

@app.route('/condominios', methods=['POST'])
def cadastrar_condominio():
    try:
        data = request.get_json()

        # Verificar campos obrigatórios
        if not data.get('nome'):
            return jsonify({"error": "Nome do condomínio é obrigatório"}), 400

        # Verificar se já existe um condomínio com o mesmo nome
        condominio_existente = Condominio.query.filter_by(nome=data['nome']).first()
        if condominio_existente:
            return jsonify({"error": "Já existe um condomínio com este nome"}), 400

        # Criar condomínio
        novo_condominio = Condominio(
            nome=data['nome']
        )

        db.session.add(novo_condominio)
        db.session.commit()

        return jsonify(novo_condominio.to_dict()), 201

    except Exception as e:
        return jsonify({"error": "Erro ao criar condomínio", "message": str(e)}), 500

@app.route('/condominios/<int:id>', methods=['GET'])
def obter_condominio(id):
    condominio = Condominio.query.get(id)
    if not condominio or not condominio.is_active:
        return jsonify({"error": "Condomínio não encontrado"}), 404
    return jsonify(condominio.to_dict())

@app.route('/condominios/<int:id>', methods=['PUT'])
def atualizar_condominio(id):
    try:
        data = request.get_json()

        # Verificar se o condomínio existe
        condominio = Condominio.query.get(id)
        if not condominio:
            return jsonify({"error": "Condomínio não encontrado"}), 404

        # Verificar se o nome já existe em outro condomínio
        if 'nome' in data and data['nome'] != condominio.nome:
            condominio_existente = Condominio.query.filter_by(nome=data['nome']).first()
            if condominio_existente:
                return jsonify({"error": "Já existe um condomínio com este nome"}), 400

        # Atualizar dados
        if 'nome' in data:
            condominio.nome = data['nome']
        if 'is_active' in data:
            condominio.is_active = data['is_active']

        db.session.commit()

        return jsonify(condominio.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "Erro ao atualizar condomínio", "message": str(e)}), 500

@app.route('/condominios/<int:id>', methods=['DELETE'])
def deletar_condominio(id):
    try:
        condominio = Condominio.query.get(id)
        if not condominio:
            return jsonify({"error": "Condomínio não encontrado"}), 404

        # Verificar se existem solicitações ativas associadas a este condomínio
        solicitacoes_ativas = Solicitacao.query.filter_by(condominio_id=id, is_deleted=False).count()
        if solicitacoes_ativas > 0:
            return jsonify({
                "error": "Não é possível excluir este condomínio pois existem solicitações associadas a ele",
                "count": solicitacoes_ativas
            }), 400

        # Desativar o condomínio ao invés de excluir
        condominio.is_active = False
        db.session.commit()

        return jsonify({"message": "Condomínio desativado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao deletar condomínio", "message": str(e)}), 500

# Rota para upload de imagem (sem alterações)
@app.route('/solicitacoes/upload', methods=['POST'])
def upload_file():
    try:
        # Verifique se há um arquivo na requisição
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
            
        file = request.files['file']
        
        # Se o usuário não selecionar um arquivo
        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Adicione timestamp para evitar conflitos de nome
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Retorne o caminho relativo
            return jsonify({"success": True, "filepath": f"/uploads/{filename}"}), 200
        else:
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400
            
    except Exception as e:
        return jsonify({"error": "Erro no upload", "message": str(e)}), 500

# Rota para servir as imagens (sem alterações)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Atualização da rota para cadastrar solicitação
@app.route('/solicitacoes', methods=['POST'])
def cadastrar_solicitacao():
    try:
        data = request.get_json()

        # Verificar campos obrigatórios
        if not data.get('nome') or not data.get('tipo'):
            return jsonify({"error": "Campos obrigatórios ausentes: nome e tipo"}), 400

        # Datas opcionais
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

        # Validar status
        status_valido = ["pendente", "confirmado", "cancelado"]
        if data.get('status') not in status_valido:
            return jsonify({"error": f"Status inválido. Escolha entre {status_valido}"}), 400

        # Criar solicitação
        nova_solicitacao = Solicitacao(
            nome=data['nome'],
            tipo=data['tipo'],
            condominio_id=data.get('condominio_id'),
            condominio=data.get('condominio'),  # Para compatibilidade 
            data_visita=data_visita,
            data_expiracao=data_expiracao,
            placa_veiculo=data.get('placa_veiculo'),
            observacoes=data.get('observacoes'),
            imagem_url=data.get('imagem_url'),
            status=data.get('status', 'pendente')  # Status padrão como 'pendente'
        )

        db.session.add(nova_solicitacao)
        db.session.commit()

        return jsonify(nova_solicitacao.to_dict()), 201

    except Exception as e:
        return jsonify({"error": "Erro ao criar solicitação", "message": str(e)}), 500


@app.route('/solicitacoes', methods=['GET'])
def listar_solicitacoes():
    try:
        # Pegar todas as solicitações que não foram deletadas
        solicitacoes = Solicitacao.query.filter_by(is_deleted=False).all()

        if not solicitacoes:
            return jsonify({"message": "Nenhuma solicitação encontrada"}), 404

        return jsonify([solicitacao.to_dict() for solicitacao in solicitacoes]), 200

    except Exception as e:
        return jsonify({"error": "Erro ao listar solicitações", "message": str(e)}), 500

@app.route('/solicitacoes/<int:id>', methods=['GET'])
def obter_solicitacao(id):
    solicitacao = Solicitacao.query.get(id)
    if not solicitacao or solicitacao.is_deleted:
        return jsonify({"error": "Solicitação não encontrada"}), 404
    return jsonify(solicitacao.to_dict())

@app.route('/solicitacoes/<int:id>', methods=['PUT'])
def atualizar_solicitacao(id):
    try:
        data = request.get_json()

        # Verificar se a solicitação existe
        solicitacao = Solicitacao.query.get(id)
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404

        # Atualizar dados
        solicitacao.nome = data.get('nome', solicitacao.nome)
        solicitacao.tipo = data.get('tipo', solicitacao.tipo)
        
        # Atualização do condomínio - priorizar o ID se estiver presente
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

        # Tratar imagem_url
        if 'imagem_url' in data:
            solicitacao.imagem_url = data['imagem_url']

        # Tratar data_visita
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

        # Tratar data_expiracao
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

        # Validar status se estiver sendo atualizado
        if 'status' in data:
            status_valido = ["pendente", "confirmado", "cancelado"]
            if data['status'] not in status_valido:
                return jsonify({"error": f"Status inválido. Escolha entre {status_valido}"}), 400
            solicitacao.status = data['status']

        db.session.commit()

        return jsonify(solicitacao.to_dict()), 200

    except Exception as e:
        return jsonify({"error": "Erro ao atualizar solicitação", "message": str(e)}), 500


@app.route('/solicitacoes/<int:id>', methods=['DELETE'])
def deletar_solicitacao(id):
    try:
        solicitacao = Solicitacao.query.get(id)
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404

        # Marcar como deletada (não deletar fisicamente)
        solicitacao.is_deleted = True
        db.session.commit()

        return jsonify({"message": "Solicitação deletada com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": "Erro ao deletar solicitação", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='192.168.1.20', port=5000)