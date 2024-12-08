from flask import Blueprint,jsonify,request
from models.doument import Document
from models import db

ingest_blueprint = Blueprint('ingest',__name__)

@ingest_blueprint.route('/test',methods = ['GET'])
def test_db_connection():
    documents = Document.query.all()
    return jsonify([{"id":doc.id,"title":doc.title,"content":doc.content} for doc in documents])

@ingest_blueprint.route('/', methods = ['POST'])
def ingest_document():
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({"error":"both title and content are required"}),400
        new_document = Document(title=title,content=content)
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

