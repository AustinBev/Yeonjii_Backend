# helpers.py
from functools import wraps
from flask import request, jsonify, json
import decimal
from models import User

def token_required(our_flask_function):
    @wraps(our_flask_function)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        current_user_token = User.query.filter_by(token=token).first()

        if current_user_token is None:
            return jsonify({'message': 'Invalid token'}), 401
        
        return our_flask_function(current_user_token, *args, **kwargs)
    return decorated

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            #Convert decimal instances into strings
            return str(obj)
        return super().default(obj)