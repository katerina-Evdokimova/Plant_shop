from flask import Flask
from data import db_session

app = Flask(__name__)
app.config.from_pyfile('config.py')
from routes import *
from login_manager import *


@app.teardown_appcontext
def shutdown_session(exception=None):
    session = db_session.create_session()
    session.close()  # Ensure any open session is closed


if __name__ == "__main__":
    
    db_session.global_init(app.config['SQLALCHEMY_DATABASE_URI'])

    app.run()
