from flask import Flask
from applications.database import db


app = None
api = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parkingdb.sqlite3"
    app.config["SECRET_KEY"] = "my_secret!"
    db.init_app(app)
    app.app_context().push()
    return app

def create_admin():
    admin = User.query.first()
    if not admin:
        admin = User(id=1,password='12345',username='Admin', phone='12345',full_name='adminn')
        db.session.add(admin)
        db.session.commit()

app = create_app()
from applications.controller import *


if __name__ == "__main__":
    db.create_all()
    create_admin()
    app.run()