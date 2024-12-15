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

# from scipy.spatial.distance import cosine


# # Cosine distance
# cosine_distance = cosine(vec1, vec2)

# print(f"Cosine Distance: {cosine_distance}")




def flatten_with_numpy(embedding):
    """Flatten a multidimensional embedding list using numpy."""
    return np.array(embedding).flatten().tolist()


async def generate_embedding_async(content):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None,embedding_pipeline,content)


def find_similar_documents(Question, top_k=5):
    """
    Retrieve the top-k most similar documents using the db object.
    """
    # Perform the query
    # print(Question.embedding)
    
#     query = (
#     db.session.query(
#         Document.id,
#         Document.title,
#         Document.content,
#         (Document.embeddings.op('<->')(Question.embedding)).label("similarity")
#     )
#     .order_by("similarity")  # Order by similarity (distance)
#     .limit(top_k)  # Limit to top-k results
# )

    query = (
        db.session.query(
            Document.id,
            Document.title,
            Document.content,
            Document.embeddings,
        )
        .limit(top_k)  # Limit to top-k results
    )
    
    # Fetch results
    results = query.all()
    # print(results)
    columns = ["id","title","content","embeddings"]
    df = pd.DataFrame(results)
    df.columns =columns
    # print(df_documents)
    
    print(type(df.at[0,'embeddings']),type(Question.embedding))
    # Stack embeddings into a numpy matrix
    document_embeddings = np.stack(df["embeddings"].values)

    # Calculate cosine similarities
    dot_products = np.dot(document_embeddings, Question.embedding)
    norms = np.linalg.norm(document_embeddings, axis=1) * np.linalg.norm(Question.embedding)
    cosine_similarities = dot_products / norms

    # Add to DataFrame and sort
    df["cosine_similarity"] = cosine_similarities
    sorted_df = df.sort_values(by="cosine_similarity", ascending=False)
    print(sorted_df)
    print(sorted_df.iloc[0])


    # Convert results to a list of dictionaries
    return [
        {"id": row.id, "name": row.title, "content": row.content}
        for row in results
    ]


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

        return find_similar_documents(question, top_k=5)
        # documents = Document.query.all()
        
        # for row in documents:
        #     Vector(row.embeddings).comparator_factory.cosine_distance(Vector(question.embedding))

        
        # return [
        #     {"id": row.id, "name": row.title, "content": row.content}#documnets
        #     for row in documents
        # ]
    except Exception as e:
        return jsonify({"error": str(e)}), 500



