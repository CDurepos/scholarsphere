from backend.app.config import Config
from backend.app.routes.search import search_bp
from backend.app.routes.recommend import recommend_bp

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(recommend_bp, url_prefix="/recommend")

    return app
