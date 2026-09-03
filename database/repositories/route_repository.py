import logging
import pymysql.cursors
from database.connection import obtener_conexion

log = logging.getLogger("route")

def get_route_by_id(route_id: int) -> dict | None:
    """
    Recupera un ruteo de la base de datos por su ID.
    """
    query = """
        SELECT * FROM route WHERE id = %s
    """
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (route_id,))
        route = cursor.fetchone()
        cursor.close()

        if route:
            log.info(f"Ruteo #{route_id} recuperado de BD.")
            return route
        else:
            log.warning(f"No se encontró ningún ruteo con ID #{route_id}.")
            return None

    except Exception as e:
        log.error(f"Error al recuperar ruteo #{route_id}: {e}")
        return None

    finally:
        if conn:
            conn.close()

def save_route(data: dict) -> dict | None:
    """
    Inserta un nuevo ruteo en la base de datos.
    """
    query = """
        INSERT INTO route (id_user, message_id, game, server, date, meeting_date, departure_date, required_dlc) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (
            data.get("id_user"),
            data.get("id_message"),
            data.get("game"),
            data.get("server"),
            data.get("date"),
            data.get("meeting_date"),
            data.get("departure_date"),
            data.get("required_dlc"),
        ))
        conn.commit()
        route_id = cursor.lastrowid
        cursor.close()

        log.info(f"Ruteo {route_id} guardado en BD.")

        return {
            "id": route_id,
            "id_user": data.get("id_user"),
            "message_id": data.get("id_message"),
            "game": data.get("game"),
            "server": data.get("server"),
            "date": data.get("date"),
            "meeting_date": data.get("meeting_date"),
            "departure_date": data.get("departure_date"),
            "required_dlc": data.get("required_dlc"),
        }
    
    except Exception as e:
        log.error(f"Error al guardar ruteo en BD: {e}")
        if conn:
            conn.rollback()
        return None
    
    finally:
        if conn:
            conn.close()

def join_route(route_id: int, user_id: int) -> bool:
    """
    Inserta un usuario en la lista de participantes de un ruteo.
    """
    query = """
        INSERT INTO route_participant (message_id, user_id)
        SELECT message_id, %s FROM route WHERE id = %s
    """
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (user_id, route_id))
        if cursor.rowcount == 0:
            conn.rollback()
            log.warning(f"No se encontró el ruteo #{route_id}.")
            return False
        conn.commit()
        cursor.close()

        log.info(f"Usuario {user_id} se ha unido al ruteo #{route_id}.")
        return True
    
    except pymysql.err.IntegrityError:
        log.warning(f"Usuario {user_id} ya estaba apuntado al ruteo #{route_id}.")
        return False
    
    except Exception as e:
        log.error(f"Error al unir usuario {user_id} al ruteo #{route_id}: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

def leave_route(route_id: int, user_id: int) -> bool:
    """
    Elimina un usuario de la lista de participantes de un ruteo.
    """
    query = """
        DELETE participant FROM route_participant AS participant JOIN route ON route.message_id = participant.message_id
        WHERE route.id = %s AND participant.user_id = %s
    """
    
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (route_id, user_id))
        conn.commit()
        cursor.close()

        log.info(f"Usuario {user_id} se ha desapuntado del ruteo #{route_id}.")
        return True
    
    except Exception as e:
        log.error(f"Error al desapuntar usuario {user_id} del ruteo #{route_id}: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

def get_route_participants(route_id: int) -> list[str]:
    """Devuelve los IDs de Discord de los participantes de un ruteo."""
    query = """
        SELECT participant.user_id
        FROM route_participant AS participant
        INNER JOIN route ON route.message_id = participant.message_id
        WHERE route.id = %s
        ORDER BY participant.id
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (route_id,))
        participants = [str(row[0]) for row in cursor.fetchall()]
        cursor.close()
        return participants

    except Exception as e:
        log.error(f"Error al obtener participantes del ruteo #{route_id}: {e}")
        return []

    finally:
        if conn:
            conn.close()