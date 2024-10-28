import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://kate:password123@localhost/plants_shop'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'secret'