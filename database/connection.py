import logging
import mariadb
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
from database.models import ALL_TABLES

log = logging.getLogger("database")

pool = None


def ensure_database_and_tables():
    """Crea la base de datos y las tablas si no existen."""
    try:
        # 1. Crear la BD si no existe
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        conn.close()

        # 2. Crear las tablas registradas en models
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        for table_query in ALL_TABLES:
            cursor.execute(table_query)
        
        conn.commit()
        cursor.close()
        conn.close()
        log.info(f"Esquema de BD verificado/creado correctamente ({DB_NAME}).")

    except mariadb.Error as e:
        log.error(f"Error al verificar/crear la BD o tablas: {e}")
        raise


def init_pool():
    global pool
    try:
        ensure_database_and_tables()

        pool = mariadb.ConnectionPool(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            pool_name="bot_pool",
            pool_size=5
        )
        log.info(f"Connection pool iniciado (host={DB_HOST}, db={DB_NAME}, pool_size=5)")
    except mariadb.Error as e:
        log.error(f"No se pudo iniciar el pool de conexiones a la BD (host={DB_HOST}, db={DB_NAME}): {e}")
        raise


def obtener_conexion():
    if pool is None:
        log.error("Se intentó obtener una conexión antes de inicializar el pool (init_pool() no se ha llamado)")
        raise RuntimeError("El pool de conexiones no está inicializado. Llama a init_pool() primero.")
    return pool.get_connection()
