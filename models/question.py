from . import db
from pgvector.sqlalchemy import Vector

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Assuming user_id comes from an authentication system
    question_text = db.Column(db.String, nullable=False)
    embedding = db.Column(Vector(1536), nullable=False)  # Vector representation of the question
    created_at = db.Column(db.DateTime, server_default = db.func.now())