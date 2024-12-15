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
import numpy as np
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch


# ingest_blueprint = Blueprint('ingest',__name__)
# app.register_blueprint(qa_blueprint,url_prefix = '/api/qa')

qa_blueprint = Blueprint('qa',__name__)
embedding_pipeline = pipeline("feature-extraction", model = 'sentence-transformers/all-MiniLM-L6-v2')
# Load T5 tokenizer and model
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")



def generate_answer(question, context):
    """
    Generate an answer based on the question and retrieved context using T5.
    """
    # Create the input prompt for T5
    prompt = f"question: {question} context: {context}"

    # Tokenize the input
    inputs = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)

    # Generate the output
    outputs = model.generate(inputs, max_length=50, num_beams=5, early_stopping=True)

    # Decode the output
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer



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
    columns = ["id","title","content","embeddings"]
    df = pd.DataFrame(results)
    df.columns =columns
    
    
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
    print(sorted_df.head(5))
    print(sorted_df.iloc[0]['content'])
    content = sorted_df.iloc[0]['content']
    return content




@qa_blueprint.route('/question', methods = ['POST','GET'])
async def qa():
    data = request.json
    question_raw = data.get("question")
    
    if not question_raw:
        return jsonify({"error": "Question is required"}), 400

    # Run the RAG pipeline
    try:
        question_embedding = await generate_embedding_async(question_raw)
        question_embedding = flatten_with_numpy(question_embedding)[:1536]

        question = Question(user_id = '84554',question_text=question_raw,embedding=question_embedding)
        try:
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            print(e)

        context =  find_similar_documents(question, top_k=5)
        answer = generate_answer(question_raw, context)
        
        return jsonify({"answer":answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



