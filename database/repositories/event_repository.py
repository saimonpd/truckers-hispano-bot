import logging
from database.connection import obtener_conexion

log = logging.getLogger("events")

def save_event(data: dict) -> bool:
    """Guarda un nuevo evento en la base de datos."""
    query = """
        INSERT INTO eventos (
            message_id, creador_id, titulo, descripcion, juego_name, juego_value,
            servidor_name, servidor_value, organizador, fecha, hora_reunion,
            hora_salida, ruta_origen, ruta_destino, link_trucksbook, link_truckersmp,
            parada_intermedio, dlcs_requeridos, carga, trailer, ruta_imagen
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    values = (
        data.get("message_id"),
        data.get("creador_id"),
        data.get("titulo"),
        data.get("descripcion"),
        data.get("juego_name"),
        data.get("juego_value"),
        data.get("servidor_name"),
        data.get("servidor_value"),
        data.get("organizador"),
        data.get("fecha"),
        data.get("hora_reunion"),
        data.get("hora_salida"),
        data.get("ruta_origen"),
        data.get("ruta_destino"),
        data.get("link_trucksbook"),
        data.get("link_truckersmp"),
        data.get("parada_intermedio"),
        data.get("dlcs_requeridos"),
        data.get("carga"),
        data.get("trailer"),
        data.get("ruta_imagen")
    )

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        log.error(f"DB Error al guardar evento: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def obtener_datos_evento(message_id: str) -> dict | None:
    """Obtiene toda la información de un evento por el ID del mensaje."""
    query = "SELECT * FROM eventos WHERE message_id = %s"
    
    conn = None
    try:
        conn = obtener_conexion()
        # dictionary=True devuelve las filas como diccionarios en lugar de tuplas
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (message_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        log.error(f"DB Error al obtener evento {message_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def obtener_lista_ids_evento(message_id: str) -> list[int]:
    """Obtiene la lista de discord_ids (enteros) apuntados al evento."""
    query = "SELECT discord_id FROM participantes_evento WHERE message_id = %s"
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (message_id,))
        rows = cursor.fetchall()
        # Convierte los IDs almacenados a int para concordar con interaction.user.id
        return [int(row[0]) for row in rows]
    except Exception as e:
        log.error(f"DB Error al obtener participantes {message_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()


def modificar_participantes_evento(message_id: str, discord_id: str, nombre: str, accion: str) -> bool:
    """Añade o elimina un participante del evento según la acción ('unirse' / 'salirse')."""
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        if accion == "unirse":
            query = """
                INSERT INTO participantes_evento (message_id, discord_id, nombre)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
            """
            cursor.execute(query, (message_id, str(discord_id), nombre))

        elif accion == "salirse":
            query = "DELETE FROM participantes_evento WHERE message_id = %s AND discord_id = %s"
            cursor.execute(query, (message_id, str(discord_id)))

        conn.commit()
        return True
    except Exception as e:
        log.error(f"DB Error al modificar participante en evento {message_id}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()