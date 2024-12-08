from . import db

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255),nullable = False)
    file_path = db.Column(db.Text,nullable = False)
    created_at = db.Column(db.DateTime,server_default = db.func.now())