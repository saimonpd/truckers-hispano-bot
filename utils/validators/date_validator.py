import re
from datetime import datetime

REGEX_FECHA = r"^\d{2}/\d{2}/\d{4}$"
REGEX_HORA = r"^([01]\d|2[0-3]):[0-5]\d$"

def _persear_fechahora(fecha_str: str, hora_str: str) -> datetime:
    """Valida la sintaxis con Regex y convierte a objeto datetime"""

    if not re.match(REGEX_FECHA, fecha_str):
        raise ValueError(f"La fecha `{fecha_str}` no tiene formato DD/MM/YYYY")

    if not re.match(REGEX_HORA, hora_str):
        raise ValueError(f"La hora `{hora_str}` no tiene formato HH:MM de 24 horas")

    try:
        return datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
    except ValueError:
        raise ValueError(f"La fecha `{fecha_str}` o la hora `{hora_str}` no existen en el calendario")

def validar_tiempos_evento(fecha: str, hora_reunion: str, hora_salida: str) -> dict: 
    """Valida reunion, salida y reglas de negocio devolviendo timestamps de discord"""

    dt_reunion = _persear_fechahora(fecha, hora_reunion)
    dt_salida = _persear_fechahora(fecha, hora_salida)

    ahora = datetime.now()

    if dt_reunion < ahora:
        raise ValueError("La fecha y hora no puede ser del pasado")

    if dt_salida <= dt_reunion:
        raise ValueError("La fecha de salida debe ser despues a la hora de reunion")

    ts_reunion = int(dt_reunion.timestamp())
    ts_salida = int(dt_salida.timestamp())

    return {
        "dt_reunion": dt_reunion,
        "dt_salida": dt_salida,
        "ts_reunion": ts_reunion,
        "ts_salida": ts_salida,
        "discord_reunion": f"<t:{ts_reunion}:F> (<t:{ts_reunion}:R>)",
        "discord_salida": f"<t:{ts_salida}:t>"
    }