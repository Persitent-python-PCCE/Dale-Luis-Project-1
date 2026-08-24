import io
import os
import pytest

def test_valid_image_file_extensions(app):
    from utils.file_upload import allowed_file

    valid_files = ["poster.png", "image.jpg", "photo.jpeg", "banner.webp", "logo.gif"]
    for filename in valid_files:
        assert allowed_file(filename) is True

def test_invalid_file_extensions(app):
    from utils.file_upload import allowed_file

    invalid_files = ["document.pdf", "script.py", "executable.exe", "notes.txt", "archive.zip", "malicious.sh"]
    for filename in invalid_files:
        assert allowed_file(filename) is False

def test_save_poster_success(app):
    from utils.file_upload import save_poster
    from werkzeug.datastructures import FileStorage

    file_obj = FileStorage(
        stream=io.BytesIO(b"fake image content"),
        filename="test_poster.png",
        content_type="image/png"
    )

    with app.app_context():
        saved_filename = save_poster(file_obj)
        assert saved_filename is not None
        assert saved_filename.endswith(".png")

def test_save_poster_invalid_extension(app):
    from utils.file_upload import save_poster
    from werkzeug.datastructures import FileStorage

    file_obj = FileStorage(
        stream=io.BytesIO(b"fake text content"),
        filename="malicious.exe",
        content_type="application/octet-stream"
    )

    with app.app_context():
        with pytest.raises(ValueError) as excinfo:
            save_poster(file_obj)
        assert "Poster must be" in str(excinfo.value)

def test_delete_poster_success(app):
    from utils.file_upload import save_poster, delete_poster
    from werkzeug.datastructures import FileStorage

    file_obj = FileStorage(
        stream=io.BytesIO(b"fake image content"),
        filename="delete_me.png",
        content_type="image/png"
    )

    with app.app_context():
        poster_path = save_poster(file_obj)
        full_path = os.path.normpath(os.path.join("static", poster_path))
        assert os.path.exists(full_path) is True

        delete_poster(poster_path)
        assert os.path.exists(full_path) is False

def test_save_user_document_success(app):
    from utils.file_upload import save_user_document, allowed_document_file
    from werkzeug.datastructures import FileStorage

    assert allowed_document_file("id_card.pdf") is True
    assert allowed_document_file("passport.png") is True

    file_obj = FileStorage(
        stream=io.BytesIO(b"fake identification pdf content"),
        filename="my_passport.pdf",
        content_type="application/pdf"
    )

    with app.app_context():
        doc_info = save_user_document(file_obj)
        assert doc_info is not None
        assert doc_info["file_name"] == "my_passport.pdf"
        assert doc_info["file_type"] == "pdf"
        assert doc_info["file_size"] > 0

        full_path = os.path.normpath(os.path.join("static", doc_info["file_path"]))
        assert os.path.exists(full_path) is True

def test_save_user_document_invalid_extension(app):
    from utils.file_upload import save_user_document
    from werkzeug.datastructures import FileStorage

    file_obj = FileStorage(
        stream=io.BytesIO(b"fake script"),
        filename="virus.sh",
        content_type="text/x-shellscript"
    )

    with app.app_context():
        with pytest.raises(ValueError) as excinfo:
            save_user_document(file_obj)
        assert "Identification document must be" in str(excinfo.value)
