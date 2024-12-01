from flask import Flask, request, jsonify, send_file
import sqlite3
import requests

app = Flask(__name__)

# Configuração do reCAPTCHA
RECAPTCHA_SECRET_KEY = 'SUA_CHAVE_SECRETA_AQUI'

# Initialize database
def init_db():
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS picks
                 (number INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def verify_recaptcha(response):
    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    return r.json()['success']

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    number = data.get('number')
    recaptcha_response = data.get('recaptcha')

    if not verify_recaptcha(recaptcha_response):
        return 'Falha na verificação do reCAPTCHA', 400

    if not 1 <= number <= 10:
        return 'Número inválido', 400

    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('INSERT INTO picks (number) VALUES (?)', (number,))
    conn.commit()
    conn.close()
    return 'Sucesso', 200

@app.route('/results')
def results():
    conn = sqlite3.connect('numbers.db')
    c = conn.cursor()
    c.execute('''SELECT number, COUNT(*) as count 
                 FROM picks 
                 GROUP BY number''')
    results = dict(c.fetchall())
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 