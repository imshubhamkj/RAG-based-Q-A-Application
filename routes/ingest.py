from flask import Blueprint, abort,jsonify,request
from models.doument import Document
from models import db
from werkzeug.utils import secure_filename
from config import Constants
import os

ingest_blueprint = Blueprint('ingest',__name__)
UPLOAD_FOLDER = Constants.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok = True)



@ingest_blueprint.route('/test',methods = ['GET'])
def test_db_connection():
    documents = Document.query.all()
    return jsonify([{"id":doc.id,"title":doc.title,"content":doc.file_path} for doc in documents])

@ingest_blueprint.route('/', methods = ['POST'])
def ingest_document():
    try:
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        # data = request.get_json()
        title = request.form.get('title')
        # content = data.get('content')
        print(file,title)

        if not title or file.filename =='':
            return jsonify({"error":"both title and file are required"}),400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER,filename)
        file.save(file_path)

        new_document = Document(title=title,file_path=file_path)
        db.session.add(new_document)
        db.session.commit()

        return jsonify({
            "message":"Document successfully ingested",
            "document_id":new_document.id
        }),201
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),500

