import discord
from config.channels import CHANNEL_EVENTS
from config.roles import ROLE_NOTIFICACION_EVENTOS
from utils.validators.date_validator import validar_tiempos_evento
from ui.embeds.event_builders import build_event_embed
from database.repositories.event_repository import (
    save_event,
    obtener_datos_evento,
    obtener_lista_ids_evento,
    modificar_participantes_evento,
)

async def _publish_on_discord(bot: discord.Client, data: dict) -> str:
    """Funcion interna del servicio encargada de enviar el Embed al canal"""
    from ui.views.event_views import EventView # Hacemos lazy import para evitar el ciclo

    channel = bot.get_channel(CHANNEL_EVENTS)
    if not channel:
        # Si no está en la caché, intentamos obtenerlo de la API
        try: 
            channel = await bot.fetch_channel(CHANNEL_EVENTS)
        except Exception:
            raise RuntimeError("No se pudo encontrar el canal de eventos en discord")


    embed = build_event_embed(data)
    view = EventView(
        link_truckersmp=data.get("link_truckersmp"),
        link_trucksbook=data.get("link_trucksbook")
    )

    msg = await channel.send(
        content=f"<@&{ROLE_NOTIFICACION_EVENTOS}>",
        embed=embed,
        view=view
    )

    return str(msg.id)

async def create_event(bot: discord.Client, data: dict) -> str:
    
    tiempos = validar_tiempos_evento(
        fecha=data["fecha"],
        hora_reunion=data["hora_reunion"],
        hora_salida=data["hora_salida"]
    )

    data.update(tiempos)
    message_id = await _publish_on_discord(bot, data)
    data["message_id"] = message_id

    success = save_event(data)
    if not success:
        raise RuntimeError("El evento se publicó en Discord pero hubo un error al guardar en BD")

    return "Evento creado y publicado con éxito en el canal."

async def toggle_participacion(message_id: str, discord_id: int, nombre: str) -> tuple[str, discord.Embed]:
    """
    Cambia el estado de participacion de usuario y devuelve texto de confirmacion junto con el Embed actualizado.
    Lo pasa al View para que lo muestre.

    Lanza:
        ValueError: si el evento no existe en la BD.
        RuntimeError: si falla la escritura en la BD.
    """
    data = obtener_datos_evento(message_id)
    if not data:
        raise ValueError("No se encontró la información de este evento en la base de datos.")

    # Recalcular timestamps de Discord, ya que no se guardan en BD.
    tiempos = validar_tiempos_evento(
        fecha=data["fecha"],
        hora_reunion=data["hora_reunion"],
        hora_salida=data["hora_salida"]
    )
    data.update(tiempos)

    participantes = obtener_lista_ids_evento(message_id)

    if discord_id in participantes:
        accion = "salirse"
        texto_respuesta = "❌ Te has desapuntado del evento."
    else:
        accion = "unirse"
        texto_respuesta = "✅ ¡Te has inscrito con éxito al evento!"

    exito = modificar_participantes_evento(
        message_id=message_id,
        discord_id=str(discord_id),
        nombre=nombre,
        accion=accion
    )
    if not exito:
        raise RuntimeError("Error al guardar tu estado en la base de datos.")

    data["participantes"] = obtener_lista_ids_evento(message_id)
    nuevo_embed = build_event_embed(data)

    return texto_respuesta, nuevo_embed