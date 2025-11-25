from backend.app.config import Config
from backend.app.routes.search import search_bp
from backend.app.routes.recommend import recommend_bp
from backend.app.routes.institution import institution_bp

from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(Config)
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(recommend_bp, url_prefix="/recommend")
    app.register_blueprint(institution_bp, url_prefix="/institution")

    return app
