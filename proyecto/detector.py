import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTOS_LOG = os.path.join(BASE_DIR, "eventos.log")
RESPUESTA_LOG = os.path.join(BASE_DIR, "respuesta.log")
FORMATO = "%Y-%m-%d %H:%M:%S"
UMBRAL = 3  # intentos fallidos que disparan la alerta


def registrar_respuesta(usuario):
    """Respuesta simulada: bloquea al usuario y deja constancia en respuesta.log."""
    fecha = datetime.now().strftime(FORMATO)

    with open(RESPUESTA_LOG, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},USUARIO_BLOQUEADO,{usuario}\n")

    return fecha


def usuarios_ya_bloqueados():
    """Usuarios que ya tienen respuesta registrada (evita responder dos veces al mismo incidente)."""
    bloqueados = set()

    if os.path.exists(RESPUESTA_LOG):
        with open(RESPUESTA_LOG, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) == 3 and partes[1] == "USUARIO_BLOQUEADO":
                    bloqueados.add(partes[2])

    return bloqueados


# ---------- Lectura de eventos ----------

intentos = {}

with open(EVENTOS_LOG, "r", encoding="utf-8") as archivo:

    for linea in archivo:

        partes = linea.strip().split(",")

        if len(partes) != 3:
            continue  # línea mal formada

        fecha, tipo, usuario = partes

        if tipo == "LOGIN_FALLIDO":

            if usuario not in intentos:
                intentos[usuario] = []

            intentos[usuario].append(fecha)

# ---------- Detección y respuesta ----------

bloqueados = usuarios_ya_bloqueados()
lista_mttd = []
lista_mttr = []

for usuario, registros in intentos.items():

    if len(registros) >= UMBRAL and usuario not in bloqueados:

        print("ALERTA DE SEGURIDAD")
        print("Usuario:", usuario)
        print("Intentos fallidos:", len(registros))
        print("Primer intento:", registros[0])
        print("Detección:", registros[UMBRAL - 1])

        # Respuesta al incidente
        fecha_respuesta = registrar_respuesta(usuario)

        print("Acción aplicada: bloqueo de usuario")
        print("Respuesta:", fecha_respuesta)

        inicio = datetime.strptime(registros[0], FORMATO)
        deteccion = datetime.strptime(registros[UMBRAL - 1], FORMATO)
        respuesta = datetime.strptime(fecha_respuesta, FORMATO)

        # MTTD: primer intento fallido -> detección (3er intento fallido)
        mttd = (deteccion - inicio).total_seconds()
        # MTTR: detección -> respuesta aplicada
        mttr = (respuesta - deteccion).total_seconds()

        print("MTTD:", mttd, "segundos")
        print("MTTR:", mttr, "segundos")
        print()

        lista_mttd.append(mttd)
        lista_mttr.append(mttr)

if lista_mttd:
    print("MTTD promedio:", round(sum(lista_mttd) / len(lista_mttd), 2), "segundos")
    print("MTTR promedio:", round(sum(lista_mttr) / len(lista_mttr), 2), "segundos")
else:
    print("Sin incidentes nuevos: ningún usuario nuevo con", UMBRAL, "o más intentos fallidos.")
