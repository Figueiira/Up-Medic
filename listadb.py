import sqlite3

def listar_usuarios():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, email, cpf, telefone FROM usuarios')
        usuarios = cursor.fetchall()

        if usuarios:
            print("Usuários cadastrados:")
            for user in usuarios:
                print(f"ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, CPF: {user[3]}, Telefone: {user[4]}")
        else:
            print("Nenhum usuário encontrado.")

if __name__ == '__main__':
    listar_usuarios()
