from flask import Flask , render_template
from flask import current_app as app
from .model import *


@app.route('/')
def login():
    return render_template('login.html')