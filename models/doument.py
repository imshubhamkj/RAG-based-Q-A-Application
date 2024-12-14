from . import db
from pgvector.sqlalchemy import Vector

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255),nullable = False)
    file_path = db.Column(db.Text,nullable = False)
    content = db.Column(db.Text,nullable = False)
    embeddings = db.Column(Vector(1536), nullable=False)
    created_at = db.Column(db.DateTime,server_default = db.func.now())