# Laboratorio: Código Seguro y Modelo OWASP

## 1. Datos generales

- **Nombre completo:** Beatriz Guadalupe Cruz de Galdamez 
- **Carné:** N/A
- **Correo institucional:** guadalupecruz1103@gmail.com
- **Asignatura:** Lenguajes de Programación con Aspectos de Seguridad
- **Fecha:** 07 de noviembre de 2026

## 2. Descripción

Este laboratorio consiste en desarrollar una aplicación web utilizando Python, implementando controles básicos de seguridad basados en buenas prácticas y el modelo OWASP. Se aplican mecanismos de validación de entradas, consultas parametrizadas, protección de contraseñas, registro de eventos de autenticación y detección de incidentes, incluyendo el cálculo de las métricas MTTD y MTTR.

## 3. Estructura del proyecto

```text
repositorio/
├── proyecto/
│   ├── app.py            # Aplicación Flask (registro, login, logs)
│   ├── crearDB.py        # Crea usuarios.db y la tabla usuarios
│   ├── detector.py       # Detección, respuesta y cálculo de MTTD/MTTR
│   ├── requirements.txt
│   ├── .gitignore
│   └── templates/
│       ├── registro.html
│       └── login.html
└── README.md
```

## 4. Ejecución del proyecto

**Paso 1.** Clonar el repositorio.

```bash
git clone URL_DEL_REPOSITORIO
```

**Paso 2.** Ingresar al proyecto.

```bash
cd repositorio/proyecto
```

**Paso 3.** Crear el entorno virtual e instalar las dependencias.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Paso 4.** Crear la base de datos (solo la primera vez).

```bash
python crearDB.py
```

**Paso 5.** Ejecutar la aplicación.

```bash
python app.py
```

Rutas disponibles: `http://127.0.0.1:5000/registro` y `http://127.0.0.1:5000/login`.

**Paso 6.** En una segunda terminal, ejecutar el detector tras generar intentos fallidos.

```bash
python detector.py
```

## 5. Controles de seguridad implementados

| Control | Implementación |
|---|---|
| Validación de usuario | 4–20 caracteres; letras, números y guion bajo |
| Validación de correo | Expresión regular de formato válido |
| Validación de contraseña | Mínimo 8 caracteres |
| Saneamiento de datos | `strip()` en usuario y correo (la contraseña no se modifica) |
| Usuarios duplicados | Consulta previa por usuario o correo |
| Protección de contraseñas | `generate_password_hash` / `check_password_hash` |
| Prevención de inyección SQL | Consultas parametrizadas (`?`) |
| Registro de eventos | `eventos.log` (LOGIN_CORRECTO / LOGIN_FALLIDO) |
| Detección de incidentes | 3 o más intentos fallidos por usuario generan alerta |
| Respuesta | Bloqueo simulado registrado en `respuesta.log` |

## 6. Resultados de MTTD y MTTR

| Prueba | Usuario | MTTD (segundos) | MTTR (segundos) |
|---|---|---|---|
| 1 | usuario_02 | 7.0 | 4.0 |
| 2 | usuario_03 | 4.0 | 6.0 |
| 3 | usuario_04 | 10.0 | 3.0 |

En cada prueba se realizaron tres intentos fallidos de inicio de sesión sobre un usuario distinto, con distinta separación entre intentos, y luego se ejecutó `detector.py`.

- **MTTD** = hora de detección (tercer intento fallido) − hora del primer intento fallido.
- **MTTR** = hora de la respuesta (bloqueo registrado en `respuesta.log`) − hora de detección.
- **MTTD promedio** = (7.0 + 4.0 + 10.0) / 3 = `7.0` segundos
- **MTTR promedio** = (4.0 + 6.0 + 3.0) / 3 = `4.33` segundos

## 7. Conclusiones

Los controles aplicados redujeron varias superficies de ataque comunes del modelo OWASP. La validación y el saneamiento de entradas rechazan datos mal formados antes de llegar a la base de datos. Las consultas parametrizadas evitan la inyección SQL: una prueba con `' OR '1'='1` fue rechazada como credenciales incorrectas. El almacenamiento de contraseñas con hash (`generate_password_hash`) impide que una filtración de `usuarios.db` exponga las claves en texto plano. La verificación de duplicados evita cuentas repetidas.

El registro de eventos en `eventos.log` aporta la visibilidad necesaria para detectar ataques de fuerza bruta. El MTTD depende directamente del tiempo entre intentos: cuando el atacante espacia sus intentos (prueba 3, MTTD de 10 s) el incidente se detecta más tarde que cuando los hace rápido (prueba 2, MTTD de 4 s). Por eso un umbral basado solo en la cantidad de intentos, sin ventana de tiempo, puede tardar en alertar ante ataques lentos.

El MTTR mide cuánto tarda la organización en contener el incidente una vez detectado. Reducirlo es importante porque, mientras no se aplica la respuesta, el atacante puede seguir probando contraseñas y una de ellas podría funcionar. En este laboratorio el detector se ejecuta de forma manual, lo que alarga el MTTR; automatizarlo (ejecución continua o bloqueo directo desde la aplicación) lo acercaría a cero y reduciría el impacto de un incidente real.
