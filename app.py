from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    CORS(app)
    from routes.ingest import ingest_blueprint
    from routes.qa import qa_blueprint
    app.register_blueprint(ingest_blueprint,url_prefix = '/api/ingest')
    app.register_blueprint(qa_blueprint,url_prefix = '/api/qa')
    
    @app.route('/')
    def navigation_form():
        return render_template('navigation.html')
    
    @app.route('/upload')
    def upload_form():
        return render_template('upload_form.html')
    
    @app.route('/ask')
    def query_form():
        return render_template('question_form.html')

    return app

if __name__=='__main__':
    app = create_app()
    app.run(debug=True)


