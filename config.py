import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://flask_user:secure_password@localhost/flask_rag"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY","default_secret_key")

class Constants:
    UPLOAD_FOLDER = '/var/tmp/uploaded_files'
