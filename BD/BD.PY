import tkinter as tk
import mysql.connector

def login():
    username = username_entry.get()
    password = password_entry.get()

    # Conexión a la base de datos MySQL
    cnx = mysql.connector.connect(
        host='192.168.44.115',
        port=3306,
        user='root',
        password='root',
        database='emma-gui'
    )
    
    # Cursor para ejecutar consultas SQL
    cursor = cnx.cursor()

    # Consulta para verificar las credenciales de inicio de sesión
    query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
    values = (username, password)
    cursor.execute(query, values)

    # Verificar si se encontró un registro en la base de datos
    if cursor.fetchone() is not None:
        print("Inicio de sesión exitoso")
    else:
        print("Credenciales inválidas")

    # Cerrar la conexión y el cursor
    cursor.close()
    cnx.close()

def create_account():
    username = username_entry.get()
    password = password_entry.get()

    # Conexión a la base de datos MySQL
    cnx = mysql.connector.connect(
        host='192.168.44.115',
        port=3306,
        user='root',
        password='root',
        database='emma-gui'
    )
    
    cursor = cnx.cursor()

    query = "SELECT * FROM usuarios WHERE username = %s"
    values = (username,)
    cursor.execute(query, values)

    if cursor.fetchone() is not None:
        print("El usuario ya existe")
    else:
        query = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
        values = (username, password)
        cursor.execute(query, values)
        cnx.commit()
        print("Cuenta creada exitosamente")

    cursor.close()
    cnx.close()

window = tk.Tk()
window.title("Inicio de sesión")
window.geometry("300x150")


username_label = tk.Label(window, text="Usuario:")
username_label.pack()
username_entry = tk.Entry(window)
username_entry.pack()

password_label = tk.Label(window, text="Contraseña:")
password_label.pack()
password_entry = tk.Entry(window, show="*")
password_entry.pack()

login_button = tk.Button(window, text="Iniciar sesión", command=login)
login_button.pack()
create_account_button = tk.Button(window, text="Crear cuenta", command=create_account)
create_account_button.pack()

window.mainloop()
