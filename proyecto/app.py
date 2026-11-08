import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")
LOG_PATH = os.path.join(BASE_DIR, "eventos.log")


@app.route("/")
def inicio():
    return "Laboratorio de Ciberseguridad"


# ---------- Validaciones (Parte 2) ----------

def validar_usuario(usuario):
    # 4 a 20 caracteres: letras, números y guion bajo
    return re.fullmatch(r"[A-Za-z0-9_]{4,20}", usuario) is not None


def validar_correo(correo):
    return re.fullmatch(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        correo
    ) is not None


def validar_password(password):
    return len(password) >= 8


# ---------- Registro de eventos (Parte 3) ----------

def registrar_evento(tipo, usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # El usuario del login no se valida; se neutralizan separadores para que
    # nadie pueda falsificar líneas del log (inyección de logs).
    usuario = re.sub(r"[,\r\n]", "_", usuario)

    with open(LOG_PATH, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},{tipo},{usuario}\n")


# ---------- Rutas ----------

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "") 

        if not validar_usuario(usuario):
            return "Usuario inválido"

        if not validar_correo(correo):
            return "Correo electrónico inválido"

        if not validar_password(password):
            return "La contraseña debe contener al menos 8 caracteres"

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM usuarios WHERE usuario = ? OR correo = ?",
            (usuario, correo)
        )

        existente = cursor.fetchone()

        if existente:
            conexion.close()
            return "El usuario o correo ya está registrado"

        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuarios (usuario, correo, password) VALUES (?, ?, ?)",
            (usuario, correo, password_hash)
        )

        conexion.commit()
        conexion.close()

        return "Usuario registrado"

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario,)
        )

        resultado = cursor.fetchone()

        conexion.close()

        if resultado and check_password_hash(resultado[3], password):
            registrar_evento("LOGIN_CORRECTO", usuario)
            return "Inicio de sesión correcto"
        else:
            registrar_evento("LOGIN_FALLIDO", usuario)
            return "Credenciales incorrectas"

    return render_template("login.html")


if __name__ == "__main__":
    # Modo debug solo si se pide explícitamente (FLASK_DEBUG=1):
    # el depurador de Werkzeug permite ejecutar código y no debe quedar activo por defecto.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
