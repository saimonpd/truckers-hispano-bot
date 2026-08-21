import discord
from config.channels import CHANNEL_EVENTS
from config.roles import ROLE_NOTIFICACION_EVENTOS
from utils.validators.date_validator import validar_tiempos_evento
from ui.embeds.event_builders import build_event_embed
from database.repositories.event_repository import save_event

async def _publish_on_discord(bot: discord.Client, data: dict) -> str:
    """Funcion interna del servicio encargada de enviar el Embed al canal"""

    channel = bot.get_channel(CHANNEL_EVENTS)
    if not channel:
        # Si no está en la caché, intentamos obtenerlo de la API
        try: 
            channel = await bot.fetch_channel(CHANNEL_EVENTS)
        except Exception:
            raise RuntimeError("No se pudo encontrar el canal de eventos en discord")


    embed = build_event_embed(data)

    msg = await channel.send(
        content=f"<@&{ROLE_NOTIFICACION_EVENTOS}>",
        embed=embed
    )

    return str(msg.id)

async def create_event(bot: discord.Client, data: dict) -> str:
    print("Estoy en el service")
    tiempos = validar_tiempos_evento(
        fecha=data["fecha"],
        hora_reunion=data["hora_reunion"],
        hora_salida=data["hora_salida"]
    )

    print("Acabo de validar las fechas")
    data.update(tiempos)
    print("Acabo de updatear las fechas en el data")
    message_id = await _publish_on_discord(bot, data)
    print("Estoy pidiendo publicar en discord")
    data["message_id"] = message_id

    success = save_event(data)
    if not success:
        raise RuntimeError("El evento se publicó en Discord pero hubo un error al guardar en BD")

    return "Evento creado y publicado con éxito en el canal."