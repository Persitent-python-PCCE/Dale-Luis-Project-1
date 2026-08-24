import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_POSTER_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[-1].lower()
    return extension in ALLOWED_POSTER_EXTENSIONS

def allowed_document_file(filename):
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[-1].lower()
    return extension in ALLOWED_DOCUMENT_EXTENSIONS

def save_poster(file):
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError("Poster must be a PNG, JPG, JPEG, WEBP, or GIF image")

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    relative_path = os.path.join("uploads", "posters", filename).replace("\\", "/")
    upload_dir = os.path.join("static", "uploads", "posters")
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return relative_path

def save_user_document(file):
    if not file or not file.filename:
        return None

    if not allowed_document_file(file.filename):
        raise ValueError("Identification document must be a PDF, PNG, JPG, JPEG, or WEBP file")

    safe_orig = secure_filename(file.filename)
    extension = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}_{safe_orig}"
    relative_path = os.path.join("uploads", "documents", filename).replace("\\", "/")
    upload_dir = os.path.join("static", "uploads", "documents")
    os.makedirs(upload_dir, exist_ok=True)
    
    full_path = os.path.join(upload_dir, filename)
    file.save(full_path)
    file_size = os.path.getsize(full_path)

    return {
        "file_path": relative_path,
        "file_name": safe_orig,
        "file_type": extension,
        "file_size": file_size
    }

def delete_poster(poster_path):
    if not poster_path:
        return
    clean_path = poster_path.replace("\\", "/")
    if clean_path.startswith("static/"):
        full_path = os.path.normpath(clean_path)
    else:
        full_path = os.path.normpath(os.path.join("static", clean_path))
    
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass
