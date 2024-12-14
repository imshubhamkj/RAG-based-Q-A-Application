import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:secure_password@localhost/flask_rag"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY","default_secret_key")

class Constants:
    UPLOAD_FOLDER = os.getcwd()+os.sep+'files'
    # print(UPLOAD_FOLDER)
