from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = ("mysql+pymysql://root:dalerioluis@localhost/online_ticket_booking")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)