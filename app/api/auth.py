import sqlalchemy as sa
from functools import wraps
from flask import abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.extensions import db
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = token_auth.current_user()
            if user is None:
                abort(401)
            if user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator