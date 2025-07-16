from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import os
from itsdangerous import URLSafeTimedSerializer
from cachelib.simple import SimpleCache
import functools

app = Flask(__name__)

#Configuração inicial
SECRET_KEY = '1235aBrcdHOKUk'
serializer = URLSafeTimedSerializer(SECRET_KEY)
cache = SimpleCache()

def generate_token(data, expiration=300):
    token = serializer.dumps(data)
    cache.set(token, data, timeout=expiration)
    return token

def validate_token(token):
    data = cache.get(token)
    if data is not None:
        return data
    return data

def token_required(f):
    @functools.wraps(f)
    def decorated_funtion(*args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        data = validate_token(token)
        if not data:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated_funtion

@app.route('/token', methods=['POST'])
def token():
    data = request.json
    token = generate_token(data)
    return jsonify({'token': token}), 200

# Diretório onde os arquivos serão salvos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Garante que a pasta de uploads exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função para verificar se o arquivo tem extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@token_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    f = request.files['file']

    if f.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400

    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)

        try:
            df = pd.read_csv(filepath, encoding='ISO-8859-1')
            return jsonify(df.to_dict(orient='records')), 200
        except Exception as e:
            return jsonify({'error': f'Erro ao ler CSV: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Arquivo não é CSV'}), 400

if __name__ == '__main__':
    app.run(debug=True)
