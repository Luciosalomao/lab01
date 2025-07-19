import os
import pandas as pd
from flask import request, jsonify
from werkzeug.utils import secure_filename
from .utils import allowed_file
from .config import Config
from .database import add_avaliacao

def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400

    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        f.save(filepath)

        try:
            df = pd.read_csv(filepath, encoding='ISO-8859-1', sep=',')
            df.columns = df.columns.str.strip()
            for _, row in df.iterrows():
                add_avaliacao(
                    row['Nome'], row['Data de hospedagem'], row['Quarto'],
                    row['Avaliacao'], int(row['Nota'])
                )
            return jsonify(df.to_dict(orient='records')), 200
        except Exception as e:
            return jsonify({'error': f'Erro ao ler CSV: {str(e)}'}), 500

    return jsonify({'error': 'Arquivo não é CSV'}), 400
