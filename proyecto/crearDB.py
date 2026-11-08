import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")

# Crear o abrir la base de datos
conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    correo TEXT,
    password TEXT
);
""")

conexion.commit()
conexion.close()

print("Base de datos y tabla creadas correctamente.")
