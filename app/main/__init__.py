from flask import Blueprint, Flask
from app.api.auth import token_auth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from config import Config
from app.extensions import db, login, limiter

login = LoginManager()

def rate_limit_key():
    try:
        user = token_auth.current_user()
        if user:
            return f"user:{user.id}"
    except Exception:
        pass
    return get_remote_address()

bp = Blueprint('main', __name__)
limiter = Limiter(key_func=rate_limit_key)

limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[]
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.limiter = limiter

    db.init_app(app)
    login.init_app(app)
    limiter.init_app(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app.main import routes
