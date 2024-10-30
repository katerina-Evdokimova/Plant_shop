from flask import Flask
from data import db_session

app = Flask(__name__)
app.config.from_pyfile('config.py')
from routes import *
from login_manager import *

db_session.global_init(app.config['SQLALCHEMY_DATABASE_URI'])


if __name__ == "__main__":
    app.run()