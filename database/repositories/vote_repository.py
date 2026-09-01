import logging
import pymysql.cursors
from database.connection import obtener_conexion

log = logging.getLogger("database")

def save_or_update_vote(suggestion_id: int, user_id: str, vote_type: str) -> bool:
    """
    Inserta o actualiza el voto de un usuario para una sugerencia en la tabla suggestion_vote.
    
    Si el usuario ya había votado, actualiza su tipo de voto.
    """
    query = """
        INSERT INTO suggestion_vote (suggestion_id, user_id, vote_type)
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

        log.info(f"Voto '{vote_type}' guardado en BD para sugerencia #{suggestion_id} por usuario {user_id}.")
        return True

    except Exception as e:
        log.error(f"Error al guardar voto en BD para sugerencia #{suggestion_id}: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def get_votes_count(suggestion_id: int) -> dict:
    """
    Obtiene el recuento de votos positivos, negativos y el total para una sugerencia.
    """
    query = """
        SELECT 
            COALESCE(SUM(CASE WHEN vote_type = 'positive' THEN 1 ELSE 0 END), 0) AS positive_votes,
            COALESCE(SUM(CASE WHEN vote_type = 'negative' THEN 1 ELSE 0 END), 0) AS negative_votes,
            COUNT(*) AS total_votes
        FROM suggestion_vote
        WHERE suggestion_id = %s
    """

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (suggestion_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {
                "positive_votes": int(result["positive_votes"]),
                "negative_votes": int(result["negative_votes"]),
                "total_votes": int(result["total_votes"])
            }
        return {"positive_votes": 0, "negative_votes": 0, "total_votes": 0}

    except Exception as e:
        log.error(f"Error al obtener recuento de votos para sugerencia #{suggestion_id}: {e}")
        return {"positive_votes": 0, "negative_votes": 0, "total_votes": 0}

    finally:
        if conn:
            conn.close()
