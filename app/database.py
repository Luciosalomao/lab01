import sqlite3

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

def get_avaliacoes():
    conn = sqlite3.connect('aula03.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM avaliacoes')
    rows = cursor.fetchall()
    conn.close()
    return [{
        'id': r[0], 'name': r[1], 'data': r[2], 'quarto': r[3],
        'avaliacao': r[4], 'nota': r[5]
    } for r in rows]
