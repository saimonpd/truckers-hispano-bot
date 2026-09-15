import logging
from database.connection import obtener_conexion

log = logging.getLogger("sanctions")


def add_sanction(mod_id: int, usuario_id: int, razon: str) -> int | None:
    """
    Inserta una sancion en la base de datos.
    Devuelve el id de la sancion creada o None si ha fallado.
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sanciones (usuario_id, mod_id, razon, fecha)
            VALUES (%s, %s, %s, NOW())
            """,
            (usuario_id, mod_id, razon)
        )
        conn.commit()

        sanction_id = cursor.lastrowid
        log.info(f"SANCTION | Sancion {sanction_id} creada para usuario {usuario_id}")
        return sanction_id

    except Exception as e:
        log.error(f"SANCTION | Error al insertar sancion en BD: {e}")
        return None
    finally:
        if conn:
            conn.close()


def delete_sanction(id_sancion: int) -> bool:
    """
    Elimina una sancion por su id.
    Devuelve True si se ha eliminado, False si no existia o ha fallado.
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM sanciones WHERE id = %s",
            (id_sancion,)
        )
        conn.commit()

        eliminado = cursor.rowcount > 0
        if eliminado:
            log.info(f"SANCTION | Sancion {id_sancion} eliminada")
        else:
            log.warning(f"SANCTION | Se intento eliminar la sancion {id_sancion} pero no existe")

        return eliminado

    except Exception as e:
        log.error(f"SANCTION | Error al eliminar sancion {id_sancion}: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_sanction(id_sancion: int) -> dict | None:
    """
    Recoge una unica sancion por id (util para mostrar el embed de confirmacion de borrado).
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, usuario_id, mod_id, razon, fecha FROM sanciones WHERE id = %s",
            (id_sancion,)
        )
        return cursor.fetchone()

    except Exception as e:
        log.error(f"SANCTION | Error al obtener sancion {id_sancion}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def user_sanctions(usuario_id: int) -> list[dict]:
    """
    Recoge todas las sanciones de un usuario.
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, usuario_id, mod_id, razon, fecha
            FROM sanciones
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            """,
            (usuario_id,)
        )
        return cursor.fetchall()

    except Exception as e:
        log.error(f"SANCTION | Error al obtener sanciones del usuario {usuario_id}: {e}")
        return []
    finally:
        if conn:
            conn.close()