from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'

# Configura o LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redireciona para login se não estiver logado

# Classe de usuário para o Flask-Login
class Usuario(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email

# Carrega o usuário com base no ID da sessão
@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return Usuario(id_=row[0], email=row[1])
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email-user']
        senha = request.form['senha']
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, email FROM usuarios WHERE email=? AND senha=?', (email, senha))
            usuario = cursor.fetchone()
            if usuario:
                user = Usuario(id_=usuario[0], email=usuario[1])
                login_user(user)
                return redirect(url_for('home'))
            else:
                return 'Login inválido. Tente novamente.'
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email-user']
        telefone = request.form['numero']
        senha = request.form['senha']
        confirma_senha = request.form['confirma_senha']

        if senha != confirma_senha:
            return 'As senhas não conferem!'

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO usuarios (nome, cpf, email, telefone, senha) VALUES (?, ?, ?, ?, ?)', 
                               (nome, cpf, email, telefone, senha))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return 'CPF ou email já cadastrado!'
    return render_template('Registro.html')

@app.route('/home')
@login_required
def home():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (current_user.id,))
        row = cursor.fetchone()
        nome = row[0] if row else "usuário"
    return render_template('index.html', nome_usuario=nome)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='192.168.0.18', port=5000, debug=True)
