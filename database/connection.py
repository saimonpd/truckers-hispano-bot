import mariadb
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

pool = None
def init_pool():
    global pool
    pool = mariadb.ConnectionPool(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME,
        port = DB_PORT,
        pool_name = "bot_pool",
        pool_size = 5
    )
    print("Connection pool iniciado")

def obtener_conexion():
    return pool.get_connection()