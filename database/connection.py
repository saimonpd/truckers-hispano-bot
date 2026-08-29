import logging
import pymysql
from dbutils.pooled_db import PooledDB
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
from database.models import ALL_TABLES

log = logging.getLogger("database")

pool = None


def ensure_database_and_tables():
    """Crea la base de datos y las tablas si no existen."""
    try:
        # 1. Crear la BD si no existe
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        conn.close()

        # 2. Crear las tablas registradas en models
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            autocommit=True
        )
        cursor = conn.cursor()
        for table_query in ALL_TABLES:
            cursor.execute(table_query)
        
        cursor.close()
        conn.close()
        log.info(f"Esquema de BD verificado/creado correctamente ({DB_NAME}).")

    except Exception as e:
        log.error(f"Error al verificar/crear la BD o tablas: {e}")
        raise


def init_pool():
    global pool
    try:
        ensure_database_and_tables()

        pool = PooledDB(
            creator=pymysql,
            mincached=1,
            maxcached=5,
            maxconnections=10,
            blocking=True,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset="utf8mb4",
            autocommit=False
        )
        log.info(f"Connection pool iniciado (host={DB_HOST}, db={DB_NAME}, pool_size=5)")
    except Exception as e:
        # Si no se puede crear pool, el bot no puede funcionar.
        log.error(f"No se pudo iniciar el pool de conexiones a la BD (host={DB_HOST}, db={DB_NAME}): {e}")
        raise


def obtener_conexion():
    if pool is None:
        # Si algo llama a obtener_conexion() antes de init_pool() queremos un 
        # error explicito en el log en vez de un AttributeError críptico.
        log.error("Se intentó obtener una conexión antes de inicializar el pool (init_pool() no se ha llamado)")
        raise RuntimeError("El pool de conexiones no está inicializado. Llama a init_pool() primero.")
    return pool.connection()
