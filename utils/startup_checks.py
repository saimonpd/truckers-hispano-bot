"""
Comprobaciones de arranque (startup checks).

Se ejecutan una vez, después de cargar todos los cogs y sincronizar los
slash commands, para verificar que las piezas externas de las que depende
el bot (base de datos, canales, roles, vistas persistentes) están
realmente disponibles antes de considerar el arranque como exitoso.

No sustituyen a un test suite (pytest) para la lógica de negocio pura
(validators, services) — esto es un chequeo de "smoke test" contra el
entorno real (Discord + BD) en el momento del arranque.
"""

import logging
import discord
from discord.ext import commands

from database.connection import obtener_conexion
from config.channels import CHANNEL_WELCOME, CHANNEL_EVENTS
from config.roles import AUTO_ROLE_ID, ENCARGADO_EVENTOS, ROLE_NOTIFICACION_EVENTOS

log = logging.getLogger("startup")


class CheckResult:
    def __init__(self, name: str, ok: bool, detail: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail


async def _check_database() -> CheckResult:
    """Comprueba que el pool de conexiones puede entregar una conexión funcional."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        return CheckResult("Base de datos", True)
    except Exception as e:
        return CheckResult("Base de datos", False, str(e))


async def _check_channel(bot: commands.Bot, channel_id: int, label: str) -> CheckResult:
    """Comprueba que un canal configurado existe y es accesible por el bot."""
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except discord.NotFound:
            return CheckResult(f"Canal '{label}'", False, f"ID {channel_id} no existe en Discord")
        except discord.Forbidden:
            return CheckResult(f"Canal '{label}'", False, f"Sin permisos para ver el canal {channel_id}")
        except Exception as e:
            return CheckResult(f"Canal '{label}'", False, str(e))
    return CheckResult(f"Canal '{label}'", True)


def _check_role(guild: discord.Guild, role_id: int, label: str) -> CheckResult:
    """Comprueba que un rol configurado existe dentro de un servidor concreto."""
    role = guild.get_role(role_id)
    if role is None:
        return CheckResult(f"Rol '{label}' en {guild.name}", False, f"ID {role_id} no existe en este servidor")
    return CheckResult(f"Rol '{label}' en {guild.name}", True)


def _check_persistent_views(bot: commands.Bot) -> CheckResult:
    """
    Comprueba las vistas persistentes registradas en main.py.

    Nota: discord.py solo añade una vista a bot.persistent_views si contiene al
    menos un componente con custom_id (botones/selects normales). Las vistas
    formadas solo por botones de tipo `link` (como WelcomeView) no generan
    interacciones hacia el bot, así que Discord no necesita "recordarlas" tras
    un reinicio y nunca aparecen aquí aunque se hayan registrado con add_view()
    sin errores. Por eso este check no compara contra "cuántas add_view() hay
    en main.py", sino que solo valida que las vistas que SÍ deberían persistir
    (las que tienen componentes con custom_id) lo hayan hecho.
    """
    nombres_registrados = {view.__class__.__name__ for view in bot.persistent_views}

    # Vistas que main.py registra y que SÍ tienen custom_id, por lo tanto
    # DEBEN aparecer en bot.persistent_views para sobrevivir a un reinicio.
    esperadas_persistentes = {"EventView"}

    faltantes = esperadas_persistentes - nombres_registrados
    if faltantes:
        return CheckResult(
            "Vistas persistentes",
            False,
            f"Faltan por registrar: {', '.join(faltantes)} (revisa main.py / los custom_id de sus botones)"
        )

    detalle = f"{', '.join(sorted(nombres_registrados))} registrada(s) correctamente"
    return CheckResult("Vistas persistentes", True, detalle)


def _check_commands_synced(bot: commands.Bot) -> CheckResult:
    """Comprueba que el árbol de comandos tiene comandos cargados antes de sincronizar."""
    comandos = bot.tree.get_commands()
    if not comandos:
        return CheckResult("Slash commands", False, "El árbol de comandos está vacío")
    nombres = ", ".join(c.name for c in comandos)
    return CheckResult("Slash commands", True, f"{len(comandos)} comando(s): {nombres}")


async def run_startup_checks(bot: commands.Bot) -> bool:
    """
    Ejecuta todas las comprobaciones de arranque y registra el resultado en el log.

    Devuelve True si todas las comprobaciones críticas pasaron, False si alguna falló.
    Los roles solo se comprueban por cada servidor en el que el bot ya está presente
    en el momento de arrancar (bot.guilds), ya que un rol es específico de un servidor.
    """
    resultados: list[CheckResult] = []

    resultados.append(await _check_database())
    resultados.append(await _check_channel(bot, CHANNEL_WELCOME, "Bienvenida"))
    resultados.append(await _check_channel(bot, CHANNEL_EVENTS, "Eventos"))
    resultados.append(_check_persistent_views(bot))
    resultados.append(_check_commands_synced(bot))

    for guild in bot.guilds:
        resultados.append(_check_role(guild, AUTO_ROLE_ID, "AUTO_ROLE_ID"))
        resultados.append(_check_role(guild, ENCARGADO_EVENTOS, "ENCARGADO_EVENTOS"))
        resultados.append(_check_role(guild, ROLE_NOTIFICACION_EVENTOS, "ROLE_NOTIFICACION_EVENTOS"))

    todo_ok = True
    log.info("── Comprobaciones de arranque ──")
    for r in resultados:
        if r.ok:
            log.info(f"  ✅ {r.name}{f' — {r.detail}' if r.detail else ''}")
        else:
            todo_ok = False
            log.error(f"  ❌ {r.name} — {r.detail}")
    log.info("─────────────────────────────────")

    return todo_ok