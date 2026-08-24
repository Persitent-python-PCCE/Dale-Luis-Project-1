from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def init_db(app):
    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        uri = os.getenv("SQLALCHEMY_DATABASE_URI")
        if not uri:
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_name = os.getenv("DB_NAME")
            uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)

