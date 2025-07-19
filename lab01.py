from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import os
from itsdangerous import URLSafeTimedSerializer
from cachelib.simple import SimpleCache
import functools
import sqlite3
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app, template_file='swagger_template.yaml')


# Configuração inicial
SECRET_KEY = '1235aBrcdHOKUk'
serializer = URLSafeTimedSerializer(SECRET_KEY)
cache = SimpleCache()

def generate_token(data, expiration=3600):
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
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token is missing'}), 401
        parts = auth_header.split(' ')
        if len(parts) != 2:
            return jsonify({'error': 'Token format inválido'}), 401
        token = parts[1]
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
            df = pd.read_csv(filepath, encoding='ISO-8859-1', sep=',')
            print("Colunas carregadas do CSV:", df.columns.tolist())

            # Remove espaços em branco nos nomes das colunas (se houver)
            df.columns = df.columns.str.strip()

            for idx, row in df.iterrows():
                add_avaliacao(
                    row['Nome'],
                    row['Data de hospedagem'],
                    row['Quarto'],
                    row['Avaliacao'],
                    int(row['Nota'])
                )

            return jsonify(df.to_dict(orient='records')), 200

        except Exception as e:
            return jsonify({'error': f'Erro ao ler CSV: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Arquivo não é CSV'}), 400
    
def init_db():
    conn = sqlite3.connect('aula03.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            data TEXT NOT NULL,
            quarto TEXT NOT NULL,            
            avaliacao TEXT NOT NULL,   
            nota INTEGER NOT NULL    
        )
    ''')
    conn.commit()
    conn.close()    

def add_avaliacao(name, data, quarto, avaliacao, nota):
    conn = sqlite3.connect('aula03.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO avaliacoes (name, data, quarto, avaliacao, nota)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, data, quarto, avaliacao, nota))
    conn.commit()
    conn.close()

@app.route('/avaliacoes', methods=['GET'])
@token_required
def get_avaliacoes():

    conn = sqlite3.connect('aula03.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM avaliacoes')
    rows = cursor.fetchall()
    conn.close()

    avaliacoes = []
    for row in rows:
        avaliacoes.append({
            'id': row[0],
            'name': row[1],
            'data': row[2],
            'quarto': row[3],
            'avaliacao': row[4],
            'nota': row[5]
        })

    return jsonify(avaliacoes), 200

init_db()

if __name__ == '__main__':
    app.run(debug=True)
