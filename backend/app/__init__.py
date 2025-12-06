from backend.app.config import Config
from backend.app.routes.auth import auth_bp
from backend.app.routes.search import search_bp
from backend.app.routes.faculty import faculty_bp
from backend.app.routes.recommend import recommend_bp
from backend.app.routes.rate_limit import rate_limit_bp
from backend.app.routes.institution import institution_bp
from backend.app.routes.equipment_search import equipment_bp


from flask_cors import CORS
from flask import Flask, Blueprint


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    app.config.from_object(Config)
    app.url_map.strict_slashes = app.config.get(
        "STRICT_SLASHES", False
    )  # If False, the trailing slash in routes and requests do not matter

    api_bp = Blueprint("api", __name__)
    
    api_bp.register_blueprint(auth_bp, url_prefix="/auth")
    api_bp.register_blueprint(search_bp, url_prefix="/search")
    api_bp.register_blueprint(faculty_bp, url_prefix="/faculty")
    api_bp.register_blueprint(recommend_bp, url_prefix="/recommend")
    api_bp.register_blueprint(rate_limit_bp, url_prefix="/rate-limit")
    api_bp.register_blueprint(institution_bp, url_prefix="/institution")
    api_bp.register_blueprint(equipment_bp, url_prefix="/equipment")

    app.register_blueprint(api_bp, url_prefix="/api")

    return app
