import logging
from database.connection import obtener_conexion

def get_suggestion_by_id(suggestion_id: int) -> dict | None:
    """
    Recupera una sugerencia de la base de datos por su ID.

    Devuelve un diccionario con los datos de la sugerencia o None si no se encuentra.
    """
    query = "SELECT * FROM suggestions WHERE id = %s"

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (suggestion_id,))
        suggestion = cursor.fetchone()
        cursor.close()

        if suggestion:
            logging.info(f"Sugerencia con ID {suggestion_id} recuperada de BD.")
            return suggestion
        else:
            logging.warning(f"No se encontró ninguna sugerencia con ID {suggestion_id}.")
            return None

    except Exception as e:
        logging.error(f"Error al recuperar la sugerencia con ID {suggestion_id}: {e}")
        return None

    finally:
        if conn:
            conn.close()

def suggestion_save(data: dict) -> dict | None:
    """
    Inserta una nueva sugerencia en la base de datos.

    Espera en `data`: id_user, title, description.
    Devuelve el dict de la sugerencia creada (con su id) o None si falla.
    """

    query = """
        INSERT INTO suggestions (id_user, id_channel, id_message, title, description)
        VALUES (%s, %s, %s, %s, %s)
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (
            data["id_user"],
            data["id_channel"],
            data["id_message"],
            data["title"],
            data["description"],
        ))
        conn.commit()
        suggestion_id = cursor.lastrowid
        cursor.close()

        logging.info(f"Sugerencia '{data['title']}' guardada en BD con id {suggestion_id}.")

        return {
            "suggestion_id": suggestion_id,
            "id_user": data["id_user"],
            "id_channel": data["id_channel"],
            "id_message": data["id_message"],
            "title": data["title"],
            "description": data["description"],
        }

    except Exception as e:
        logging.error(f"Error al guardar la sugerencia '{data.get('title')}' en BD: {e}")
        return None

    finally:
        if conn:
            conn.close()

def update_vote(suggestion_id: int, user_id: str, vote_type: str) -> bool:
    """
    Actualiza el voto de un usuario para una sugerencia específica.
    """
    
    query = """
        INSERT INTO suggestion_votes (suggestion_id, user_id, vote_type)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type)
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (suggestion_id, user_id, vote_type))
        conn.commit()
        cursor.close()

        logging.info(f"Voto '{vote_type}' registrado para la sugerencia {suggestion_id} por el usuario {user_id}.")
        return True

    except Exception as e:
        logging.error(f"Error al actualizar el voto para la sugerencia {suggestion_id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()

def update_suggestion_status(suggestion_id: int, status: str, moderator_id: str, moderator_name: str, moderator_answer: str) -> bool:
    """
    Actualiza el estado de una sugerencia en la base de datos.

    Devuelve True si la actualización fue exitosa, False en caso contrario.
    """
    query = """
        UPDATE suggestions
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

        logging.info(f"Estado de la sugerencia {suggestion_id} actualizado a '{status}' por el moderador {moderator_name}.")
        return True

    except Exception as e:
        logging.error(f"Error al actualizar el estado de la sugerencia {suggestion_id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()