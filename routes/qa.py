from flask import Blueprint, abort,jsonify,request
from models.doument import Document
from models.question import Question
from models import db
from werkzeug.utils import secure_filename
from config import Constants
import os,asyncio
import numpy as np
from transformers import pipeline
from sqlalchemy import func,text
from pgvector.sqlalchemy import Vector
import pandas as pd

# ingest_blueprint = Blueprint('ingest',__name__)
# app.register_blueprint(qa_blueprint,url_prefix = '/api/qa')

qa_blueprint = Blueprint('qa',__name__)
embedding_pipeline = pipeline("feature-extraction", model = 'sentence-transformers/all-MiniLM-L6-v2')

from scipy.spatial.distance import cosine


# Cosine distance
cosine_distance = cosine(vec1, vec2)

print(f"Cosine Distance: {cosine_distance}")




def flatten_with_numpy(embedding):
    """Flatten a multidimensional embedding list using numpy."""
    return np.array(embedding).flatten().tolist()


async def generate_embedding_async(content):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None,embedding_pipeline,content)


@qa_blueprint.route('/question', methods = ['POST','GET'])
async def qa():
    data = request.json
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Run the RAG pipeline
    try:
        question_embedding = await generate_embedding_async(question)
        question_embedding = flatten_with_numpy(question_embedding)[:1536]

        question = Question(user_id = '84554',question_text=question,embedding=question_embedding)
        try:
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            print(e)

        documents = Document.query.all()
        
        for row in documents:
            Vector(row.embeddings).comparator_factory.cosine_distance(Vector(question.embedding))

        
        return [
            {"id": row.id, "name": row.title, "content": row.content}#documnets
            for row in documents
        ]
    except Exception as e:
        return jsonify({"error": str(e)}), 500



