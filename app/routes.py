from flask import Blueprint, request, jsonify
from .auth import generate_token, token_required
from .upload import handle_upload
from .database import get_avaliacoes

bp = Blueprint('routes', __name__)

@bp.route('/token', methods=['POST'])
def token():
    data = request.json
    token = generate_token(data)
    return jsonify({'token': token}), 200

@bp.route('/upload', methods=['POST'])
@token_required
def upload():
    return handle_upload()

@bp.route('/avaliacoes', methods=['GET'])
@token_required
def avaliacoes():
    return jsonify(get_avaliacoes()), 200
