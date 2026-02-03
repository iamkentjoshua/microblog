from app.extensions import db, limiter
from app.api import bp
from app.api.auth import basic_auth, token_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
@limiter.limit("5 per minute")
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
@limiter.limit("10 per minute")
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204