import os
import logging
from dotenv import load_dotenv

log = logging.getLogger("config")

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    log.error("Falta la variable de entorno TOKEN. Revisa tu archivo .env (basado en .env.example).")
    raise ValueError("La variable de entorno TOKEN es obligatoria y no está definida.")

# DATABASE
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

_faltantes_db = [
    nombre for nombre, valor in [
        ("DB_USER", DB_USER),
        ("DB_PASSWORD", DB_PASSWORD),
        ("DB_NAME", DB_NAME),
    ] if not valor
]
if _faltantes_db:
    log.error(f"Faltan variables de entorno de base de datos: {', '.join(_faltantes_db)}")
    raise ValueError(f"Variables de entorno de base de datos incompletas: {', '.join(_faltantes_db)}")

log.info("Configuración cargada correctamente desde el entorno")