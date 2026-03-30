import os
from datetime import datetime

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename

from ..utils.file_utils import allowed_file, get_file_type

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/solicitacoes/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_extension = filename.rsplit('.', 1)[1].lower()
            filename_without_ext = filename.rsplit('.', 1)[0]
            new_filename = f"{timestamp}_{filename_without_ext}.{file_extension}"

            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
            file.save(filepath)

            file_type = get_file_type(new_filename)

            return jsonify({
                "success": True,
                "filepath": f"/uploads/{new_filename}",
                "file_type": file_type,
                "original_filename": file.filename,
                "size": os.path.getsize(filepath)
            }), 200
        else:
            return jsonify({
                "error": "Tipo de arquivo não permitido. Apenas imagens e PDFs são aceitos"
            }), 400

    except Exception as e:
        return jsonify({"error": "Erro no upload", "message": str(e)}), 500


@uploads_bp.route('/solicitacoes/upload-multiple', methods=['POST'])
def upload_multiple_files():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        files = request.files.getlist('files')

        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        uploaded_files = []
        errors = []

        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_extension = filename.rsplit('.', 1)[1].lower()
                filename_without_ext = filename.rsplit('.', 1)[0]
                new_filename = f"{timestamp}_{filename_without_ext}.{file_extension}"

                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                file.save(filepath)

                file_type = get_file_type(new_filename)

                uploaded_files.append({
                    "filepath": f"/uploads/{new_filename}",
                    "file_type": file_type,
                    "original_filename": file.filename,
                    "size": os.path.getsize(filepath)
                })
            else:
                errors.append(f"Arquivo '{file.filename}' não é permitido")

        if uploaded_files:
            return jsonify({
                "success": True,
                "uploaded_files": uploaded_files,
                "errors": errors if errors else None
            }), 200
        else:
            return jsonify({"error": "Nenhum arquivo válido", "details": errors}), 400

    except Exception as e:
        return jsonify({"error": "Erro no upload múltiplo", "message": str(e)}), 500


@uploads_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@uploads_bp.route('/uploads/<filename>/info')
def file_info(filename):
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(filepath):
            return jsonify({"error": "Arquivo não encontrado"}), 404

        file_stats = os.stat(filepath)
        file_type = get_file_type(filename)

        return jsonify({
            "filename": filename,
            "file_type": file_type,
            "size": file_stats.st_size,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except Exception as e:
        return jsonify({"error": "Erro ao obter informações", "message": str(e)}), 500