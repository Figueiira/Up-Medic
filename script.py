import sqlite3

def criar_tabela_agendamentos():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data TEXT NOT NULL,
        horario TEXT NOT NULL,
        especialidade TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print("Tabela 'agendamentos' criada com sucesso (ou já existia).")

if __name__ == '__main__':
    criar_tabela_agendamentos()
