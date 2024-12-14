from flask import Blueprint, abort,jsonify,request
from models.doument import Document
from models import db
from werkzeug.utils import secure_filename
from config import Constants
import os,asyncio
import numpy as np
from transformers import pipeline


ingest_blueprint = Blueprint('ingest',__name__)
UPLOAD_FOLDER = Constants.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

#Initialize embedding pipeline
embedding_pipeline = pipeline("feature-extraction", model = 'sentence-transformers/all-MiniLM-L6-v2')


def flatten_with_numpy(embedding):
    """Flatten a multidimensional embedding list using numpy."""
    return np.array(embedding).flatten().tolist()


async def generate_embedding_async(content):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None,embedding_pipeline,content)


@ingest_blueprint.route('/test',methods = ['GET'])
def test_db_connection():
    documents = Document.query.all()
    return jsonify([{"id":doc.id,"title":doc.title,"content":doc.content,"file_path":doc.file_path} for doc in documents])

@ingest_blueprint.route('/', methods = ['POST'])
async def ingest_document():
    try:
        print("in ingest documents")
        print(request.files)
        if 'file' not in request.files:
            abort(400)
        print(request)
        file = request.files['file']
        print('file')
        # data = request.get_json()
        title = request.form.get('title')
        # content = data.get('content')
        print(file,title)

        if not title or file.filename =='':
            return jsonify({"error":"both title and file are required"}),400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER,filename)
        file.save(file_path)
        content = ''
        with open(file_path,'r') as file:
            content = file.read()
        
        embeddings = await generate_embedding_async(content)
        embeddings = list(flatten_with_numpy(embeddings))[:1536]
        
        

        new_document = Document(title=title,file_path=file_path,content=content,embeddings=embeddings)
        try:
            db.session.add(new_document)
            db.session.commit()
        except Exception as e:
            print(e)

        return jsonify({
            "message":"Document successfully ingested",
            "document_id":new_document.id
        }),201
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),500

