from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Usuario(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email


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
            cursor.execute('SELECT id, email, senha FROM usuarios WHERE email = ?', (email,))
            usuario = cursor.fetchone()
            if usuario and check_password_hash(usuario[2], senha):
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

        senha_hash = generate_password_hash(senha)

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO usuarios (nome, cpf, email, telefone, senha) VALUES (?, ?, ?, ?, ?)', 
                               (nome, cpf, email, telefone, senha_hash))
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

@app.route('/historico')
@login_required
def historico():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (current_user.id,))
        row = cursor.fetchone()
        nome = row[0] if row else "usuario"
    return render_template('historico.html', nome_usuario=nome )

# Dados fixos disponibilidades e especialidades
DISPONIBILIDADES = {
    '2025-06-13': ['08:00', '09:00', '10:00'],
    '2025-06-14': ['11:00', '12:00'],
    '2025-06-15': ['14:00', '15:00', '16:00'],
    '2025-06-16': ['08:00', '09:30'],
    '2025-06-17': ['13:00', '14:30'],
    '2025-06-18': ['15:00', '16:00'],
    '2025-06-19': ['10:00', '11:00', '13:00'],
    '2025-06-20': ['09:00', '12:00'],
    '2025-06-21': ['08:00', '09:00'],
    '2025-06-22': ['14:00', '15:00']
}

ESPECIALIDADES = ['Cardiologia', 'Dermatologia', 'Pediatria', 'Ortopedia']

# Lista em memória para armazenar agendamentos
agendamentos = []

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    data_selecionada = None
    horarios_disponiveis = []

    if request.method == 'POST':
        data_selecionada = request.form.get('data')
        # Atualizar horários disponíveis ao escolher data
        if data_selecionada:
            horarios_disponiveis = DISPONIBILIDADES.get(data_selecionada, [])

        # Se o usuário já escolheu horário (agendamento final)
        if 'horario' in request.form and request.form.get('horario'):
            nome = request.form.get('nome')
            horario = request.form.get('horario')
            especialidade = request.form.get('especialidade')

            if horario not in horarios_disponiveis:
                flash('Horário indisponível.', 'error')
                return redirect(url_for('agendar'))

            # Salvar agendamento
            agendamentos.append({
                'nome': nome,
                'data': data_selecionada,
                'horario': horario,
                'especialidade': especialidade,
                'usuario_id': current_user.id
            })

            flash('Agendamento realizado com sucesso!', 'success')
            return redirect(url_for('consultas_marcadas'))

    return render_template(
        'agendar.html',
        disponibilidades=DISPONIBILIDADES,
        especialidades=ESPECIALIDADES,
        data_selecionada=data_selecionada,
        horarios_disponiveis=horarios_disponiveis
    )

@app.route('/consultas_marcadas')
@login_required
def consultas_marcadas():
    # Filtra os agendamentos só do usuário logado (se quiser separar)
    user_agendamentos = [a for a in agendamentos if a['usuario_id'] == current_user.id]
    return render_template('consultas_marcadas.html', agendamentos=user_agendamentos)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
