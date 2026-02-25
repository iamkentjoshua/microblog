from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
login = LoginManager()
babel = Babel()

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

def rate_limit_key():
    try:
        from app.api.auth import token_auth
        user = token_auth.current_user()
        if user:
            return f"user:{user.id}"
    except Exception:
        pass
    return get_remote_address()

limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=[]
)