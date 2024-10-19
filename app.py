from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
import requests
import json
import uuid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

app = Flask(__name__)
app.secret_key ='rivs'
app_session_token = str(uuid.uuid4())

# Função para inicializar o banco de dados
def init_db():
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password TEXT NOT NULL,
                saldo REAL DEFAULT 0
            )
        ''')
        conn.commit()

# Inicializar o banco de dados ao iniciar a aplicação
init_db()

### Funções de Apoio ###
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
@app.before_request
def validate_session():
    global app_session_token
    session_token = session.get('app_session_token')
    if session_token!= app_session_token:
        session.clear()  # Encerre a sessão se o token não corresponder

### Rotas ###
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('gerador'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not password:
            flash('Por favor, informe a senha.', 'danger')
            return render_template('login.html')
        
        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE username =?', (username,))
            user = cursor.fetchone()
            
            if user:
                try:
                    ph.verify(user[3], password)
                    session['user'] = username
                    session['app_session_token'] = app_session_token
                    #flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('gerador'))
                except VerifyMismatchError:
                    flash('Senha incorreta.', 'danger')
            else:
                flash('Usuário não encontrado.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hashed = ph.hash(password)
        
        try:
            with sqlite3.connect('usuarios.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO usuarios (username, email, password, saldo) VALUES (?,?,?,?)', (username, email, password_hashed, 0.0))
                conn.commit()
                flash('Usuário cadastrado com sucesso! Agora você pode fazer login.', 'uccess')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe. Tente outro.', 'danger')
    
    return render_template('register.html')

@app.route('/gerador', methods=['GET', 'POST'])
def gerador():
    if 'user' not in session or 'app_session_token' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
    
    consulta_resultado = None
    saldo = 0.0
    
    if request.method == 'POST':
        # Verificar o saldo do usuário
        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT saldo FROM usuarios WHERE username =?', (session.get('user'),))
            row = cursor.fetchone()
            if not row or row[0] < 1:
                flash('Sem saldo para gerar CPF.', 'danger')
                return redirect(url_for('gerador'))
        
        # Dados para a requisição ao 4devs
        payload = {
            'acao': 'gerar_pessoa',
            'exo': 'I',
            'pontuacao': 'N',
            'idade': '0',
            'cep_estado': '',
            'txt_qtde': '1',
            'cep_cidade': ''
        }
        
        # Faz a requisição POST para o site do 4devs
        response = requests.post('https://www.4devs.com.br/ferramentas_online.php', data=payload)
        
        if response.status_code == 200:
            try:
                consulta_resultado = response.json()
                flash('Geração de pessoa realizada com sucesso.', 'uccess')
                
                # Debitar 1 crédito do saldo do usuário
                with sqlite3.connect('usuarios.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('UPDATE usuarios SET saldo = saldo - 1 WHERE username =?', (session.get('user'),))
                    conn.commit()
            except ValueError:
                flash('Não foi possível interpretar a resposta da geração de pessoas.', 'danger')
        else:
            flash('Falha ao realizar a geração de pessoas.', 'danger')
    
    # Obtenha o saldo do usuário aqui
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT saldo FROM usuarios WHERE username =?', (session.get('user'),))
        row = cursor.fetchone()
        if row:
            saldo = row[0]
    
    return render_template('gerador.html', resultado=consulta_resultado, user=session.get('user'), saldo=saldo)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or session['user']!= 'rivs':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('login'))
    
    usuarios = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        
        if action == 'update':
            novo_saldo = float(request.form['saldo'])
            with sqlite3.connect('usuarios.db') as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET saldo =? WHERE username =?', (novo_saldo, username))
                conn.commit()
            flash(f'Saldo do usuário {username} atualizado com sucesso.', 'uccess')
        
        elif action == 'add':
            email = request.form['email']
            password = request.form['password']
            password_hashed = ph.hash(password)
            try:
                with sqlite3.connect('usuarios.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO usuarios (username, email, password, saldo) VALUES (?,?,?,?)',
                                   (username, email, password_hashed, 0.0))
                    conn.commit()
                    flash(f'Usuário {username} adicionado com sucesso.', 'uccess')
            except sqlite3.IntegrityError:
                flash('Nome de usuário já existe. Tente outro.', 'danger')
        
        elif action == 'delete':
            with sqlite3.connect('usuarios.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM usuarios WHERE username =?', (username,))
                conn.commit()
            flash(f'Usuário {username} removido com sucesso.', 'uccess')
    
    # Carregar lista de usuários
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, saldo FROM usuarios')
        usuarios = cursor.fetchall()
    
    return render_template('admin.html', usuarios=usuarios)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.static_folder = 'static'
    app.run(debug=True)