import logging
import pymysql.cursors
from database.connection import obtener_conexion

log = logging.getLogger("database")


def get_suggestion_by_id(suggestion_id: int) -> dict | None:
    """
    Recupera una sugerencia de la base de datos por su ID junto con sus votos de suggestion_vote.
    """
    query = """
        SELECT 
            s.*,
            COALESCE(SUM(CASE WHEN v.vote_type = 'positive' THEN 1 ELSE 0 END), 0) AS positive_votes,
            COALESCE(SUM(CASE WHEN v.vote_type = 'negative' THEN 1 ELSE 0 END), 0) AS negative_votes
        FROM suggestion s
        LEFT JOIN suggestion_vote v ON s.id = v.suggestion_id
        WHERE s.id = %s
        GROUP BY s.id
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (suggestion_id,))
        suggestion = cursor.fetchone()
        cursor.close()

        if suggestion:
            log.info(f"Sugerencia con ID #{suggestion_id} recuperada de BD.")
            return suggestion
        else:
            log.warning(f"No se encontró ninguna sugerencia con ID #{suggestion_id}.")
            return None

    except Exception as e:
        log.error(f"Error al recuperar sugerencia #{suggestion_id}: {e}")
        return None

    finally:
        if conn:
            conn.close()

def suggestion_save(data: dict) -> dict | None:
    """
    Inserta una nueva sugerencia en la base de datos.
    """
    query = """
        INSERT INTO suggestion (id_user, id_channel, id_message, description)
        VALUES (%s, %s, %s, %s)
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (
            data["id_user"],
            data["id_channel"],
            data["id_message"],
            data["description"],
        ))
        conn.commit()
        suggestion_id = cursor.lastrowid
        cursor.close()

        log.info(f"Sugerencia {suggestion_id} guardada en BD.")

        return {
            "suggestion_id": suggestion_id,
            "id": suggestion_id,
            "id_user": data["id_user"],
            "id_channel": data["id_channel"],
            "id_message": data["id_message"],
            "description": data["description"],
            "positive_votes": 0,
            "negative_votes": 0,
            "status": "Pendiente",
        }

    except Exception as e:
        log.error(f"Error al guardar sugerencia en BD: {e}")
        if conn:
            conn.rollback()
        return None

    finally:
        if conn:
            conn.close()


def update_suggestion_status(suggestion_id: int, status: str, moderator_id: str, moderator_name: str, moderator_answer: str) -> bool:
    """
    Actualiza el estado y respuesta de una sugerencia en la base de datos.
    """
    query = """
        UPDATE suggestion
        SET status = %s,
            moderator_id = %s,
            moderator_name = %s,
            moderator_answer = %s
        WHERE id = %s
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (status, moderator_id, moderator_name, moderator_answer, suggestion_id))
        conn.commit()
        cursor.close()

        log.info(f"Estado de sugerencia #{suggestion_id} actualizado a '{status}' por {moderator_name}.")
        return True

    except Exception as e:
        log.error(f"Error al actualizar estado de sugerencia #{suggestion_id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()