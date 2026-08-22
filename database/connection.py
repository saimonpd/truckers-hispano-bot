import logging
import mariadb
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
log = logging.getLogger("database")

pool = None

def init_pool():
    global pool
    try:
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
        # Si no se puede crear pool, el bot no puede funcionar.
        log.error(f"No se pudo iniciar el pool de conexiones a la BD (host={DB_HOST}, db={DB_NAME}): {e}")
        raise


def obtener_conexion():
    if pool is None:
        # Si algo llama a obtener_conexion() antes de init_pool() queremos un 
        # error explicito en el log en vez de un AttributeError críptico.
        log.error("Se intentó obtener una conexión antes de inicializar el pool (init_pool() no se ha llamado)")
        raise RuntimeError("El pool de conexiones no está inicializado. Llama a init_pool() primero.")
    return pool.get_connection()