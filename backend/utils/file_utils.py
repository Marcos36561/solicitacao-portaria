from flask import current_app


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def is_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['IMAGE_EXTENSIONS']


def is_pdf_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['PDF_EXTENSIONS']


def get_file_type(filename):
    if is_image_file(filename):
        return 'image'
    elif is_pdf_file(filename):
        return 'pdf'
    return 'unknown'