from flask import request, jsonify
from itsdangerous import URLSafeTimedSerializer
from cachelib.simple import SimpleCache
import functools
from .config import Config

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
cache = SimpleCache()

def generate_token(data, expiration=3600):
    token = serializer.dumps(data)
    cache.set(token, data, timeout=expiration)
    return token

def validate_token(token):
    return cache.get(token)

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({'error': 'Token is missing'}), 401
        parts = auth.split()
        if len(parts) != 2:
            return jsonify({'error': 'Token format inválido'}), 401
        token = parts[1]
        data = validate_token(token)
        if not data:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated
