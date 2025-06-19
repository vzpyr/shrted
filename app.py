import string
import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '42886825-6305-4d9b-b8b7-45b8ab1384d2'

def get():
    conn = sqlite3.connect('shrted.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def exists(code):
    db = get()
    cur = db.execute('SELECT 1 FROM urls WHERE code = ?', (code,))
    return cur.fetchone() is not None

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        long_url = request.form.get('long_url')
        if not long_url:
            flash('you didn\'t enter anything', 'error')
        else:
            code = generate()
            while exists(code):
                code = generate()
            db = get()
            db.execute('INSERT INTO urls (code, long_url) VALUES (?, ?)', (code, long_url))
            db.commit()
            short_url = request.host_url + code
    return render_template('index.html', short_url=short_url)

@app.route('/<code>')
def redirect_to_url(code):
    db = get()
    cur = db.execute('SELECT long_url FROM urls WHERE code = ?', (code,))
    row = cur.fetchone()
    return redirect(row['long_url'])

if __name__ == '__main__':
    with get() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                long_url TEXT NOT NULL
            )
        ''')
    app.run()