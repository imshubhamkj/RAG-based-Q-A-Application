from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    CORS(app)
    from routes.ingest import ingest_blueprint
    # from routes.qa import qa_blueprint
    app.register_blueprint(ingest_blueprint,url_prefix = '/api/ingest')
    # app.register_blueprint(qa_blueprint,url_prefix = '/api/qa')
    return app

if __name__=='__main__':
    app = create_app()
    app.run(debug=True)


