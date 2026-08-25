import logging
from database.connection import obtener_conexion


def guardar_empresa(data: dict) -> dict | None:
    """
    Inserta una nueva empresa en la base de datos.

    Espera en `data`: nombre_empresa, dueño_empresa, rol_id, canal_id.
    Devuelve el dict de la empresa creada (con su id) o None si falla.
    """
    query = """
        INSERT INTO empresas (nombre_empresa, dueño_empresa, rol_id, canal_id)
        VALUES (%s, %s, %s, %s)
    """
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (
            data["nombre_empresa"],
            data["dueño_empresa"],
            data["rol_id"],
            data["canal_id"],
        ))
        conn.commit()
        empresa_id = cursor.lastrowid
        cursor.close()

        logging.info(f"Empresa '{data['nombre_empresa']}' guardada en BD con id {empresa_id}.")

        return {
            "empresa_id": empresa_id,
            "nombre_empresa": data["nombre_empresa"],
            "dueño_empresa": data["dueño_empresa"],
            "rol_id": data["rol_id"],
            "canal_id": data["canal_id"],
        }

    except Exception as e:
        logging.error(f"Error al guardar la empresa '{data.get('nombre_empresa')}' en BD: {e}")
        return None

    finally:
        if conn:
            conn.close()


def obtener_datos_empresa(empresa_id: str) -> dict | None:
    """Recupera los datos de una empresa por su id. Devuelve None si no existe."""
    query = "SELECT * FROM empresas WHERE empresa_id = %s"
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (empresa_id,))
        row = cursor.fetchone()
        columnas = [desc[0] for desc in cursor.description]
        cursor.close()

        if row is None:
            return None

        return dict(zip(columnas, row))

    except Exception as e:
        logging.error(f"Error al obtener la empresa '{empresa_id}' de BD: {e}")
        return None

    finally:
        if conn:
            conn.close()


def obtener_empresa_por_rol_id(rol_id: str) -> dict | None:
    """Recupera los datos de una empresa a partir del id de su rol. Devuelve None si no existe."""
    query = "SELECT * FROM empresas WHERE rol_id = %s"
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (rol_id,))
        row = cursor.fetchone()
        columnas = [desc[0] for desc in cursor.description]
        cursor.close()

        if row is None:
            return None

        return dict(zip(columnas, row))

    except Exception as e:
        logging.error(f"Error al obtener la empresa con rol_id '{rol_id}' de BD: {e}")
        return None

    finally:
        if conn:
            conn.close()


def eliminar_empresa_bd(empresa_id: str) -> bool:
    """Elimina el registro de una empresa por su id. Devuelve True si se borró correctamente."""
    query = "DELETE FROM empresas WHERE empresa_id = %s"
    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query, (empresa_id,))
        conn.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()

        if filas_afectadas == 0:
            logging.warning(f"Se intentó borrar la empresa '{empresa_id}' pero no existía en BD.")
            return False

        logging.info(f"Empresa '{empresa_id}' eliminada de BD.")
        return True

    except Exception as e:
        logging.error(f"Error al eliminar la empresa '{empresa_id}' de BD: {e}")
        return False

    finally:
        if conn:
            conn.close()