from flask import Flask   # Imports the Flask class (needed to create the application) and the SQLAlchemy database instance
from applications.database import db


app = None
api = None

def create_app(): # Defines a function that creates and configures the Flask application.
    app = Flask(__name__) # Creates a new Flask application instance, handling web requests
    app.debug = True # Enables debug mode, which provides detailed error pages and auto-reloads the server on code changes.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parkingdb.sqlite3" # Configures the database connection to use SQLite with a file named parkingdb.sqlite3 for storing data
    app.config["SECRET_KEY"] = "my_secret!" # Sets a secret key needed for securely signing session cookies and other security features preventing from security attacks
    db.init_app(app) # Connects the SQLAlchemy database instance with the Flask application.
    app.app_context().push() # Pushes an application context, which is needed for certain Flask operations
    return app

def create_admin():
    admin = User.query.first()
    if not admin:
        admin = User(id=1,password='12345',username='Admin@gmail.com', phone='12345',full_name='adminn')
        db.session.add(admin)
        db.session.commit()

app = create_app()
from applications.controller import *


if __name__ == "__main__":
    db.create_all()
    create_admin()
    app.run()