from config.roles import ROLE_NOTIFICACION_RUTEOS
from utils.validators.date_validator import validar_tiempos_evento
import discord
import logging
from database.repositories.route_repository import (save_route, get_route_by_id)
from ui.embeds.route_builders import build_route_embed

log = logging.getLogger("route")

async def route_create(channel: discord.TextChannel, interaction: discord.Interaction, data: dict) -> dict:
    try:
        data["id_user"] = str(data["author_id"])
        data["guild_id"] = str(data["guild_id"])

        tiempos = validar_tiempos_evento(
            fecha=data["date"],
            hora_reunion=data["meeting_date"],
            hora_salida=data["departure_date"]
        )
        data.update(tiempos)
        
        message_id, message, view = await _publish_on_discord(channel, data)
        data["id_message"] = message_id

        # Llamada al repositorio para guardar el ruteo en la base de datos
        route = save_route(data)
        if not route:
            try:
                await message.delete()
            except Exception:
                pass
            raise RuntimeError("No se pudo guardar el ruteo en la base de datos.")
        
        view.route_id = route["id"]
        
        return route

    except ValueError as e:
        raise ValueError(e)

    except Exception as e:
        log.error(f"Error creando ruta: {e}")
        raise RuntimeError("Error creando ruta.")

async def route_join(route_id: int, user_id: int):
    from database.repositories.route_repository import join_route

    try:
        success = join_route(route_id, user_id)
        if not success:
            raise RuntimeError("No se pudo apuntar al ruteo.")

        route_data = get_route_by_id(route_id)
        if not route_data:
            raise RuntimeError("No se ha encontrado el ruteo en la base de datos")

        tiempos = validar_tiempos_evento(
            fecha=route_data["date"],
            hora_reunion=route_data["meeting_date"],
            hora_salida=route_data["departure_date"]
        )
        route_data.update(tiempos)

        participants_id = get_route_participants(route_id)
        route_data["participants"] = participants_id

        updated = build_route_embed(route_data)

        return updated

    except Exception as e:
        log.error(f"Error apuntando al ruteo #{route_id}: {e}")
        raise RuntimeError("Error apuntando al ruteo.")

async def route_leave(route_id: int, user_id: int):
    from database.repositories.route_repository import leave_route

    try:
        success = leave_route(route_id, user_id)
        if not success:
            raise RuntimeError("No se pudo desapuntar del ruteo.")

        route_data = get_route_by_id(route_id)
        if not route_data:
            raise RuntimeError("No se ha encontrado el ruteo en la base de datos")

        tiempos = validar_tiempos_evento(
            fecha=route_data["date"],
            hora_reunion=route_data["meeting_date"],
            hora_salida=route_data["departure_date"]
        )
        route_data.update(tiempos)

        participants_id = get_route_participants(route_id)
        route_data["participants"] = participants_id

        updated = build_route_embed(route_data)

        return updated
    
    except Exception as e:
        log.error(f"Error desapuntando del ruteo #{route_id}: {e}")
        raise RuntimeError("Error desapuntando del ruteo.")

def get_route_participants(route_id: int) -> list[str]:
    from database.repositories.route_repository import get_route_participants as repository_get_participants

    return repository_get_participants(route_id)

async def _publish_on_discord(channel: discord.TextChannel, data: dict) -> tuple[str, discord.Message, discord.ui.View]:
    from ui.views.route_views import RouteView
    
    embed = build_route_embed(data)
    view = RouteView(data)

    msg = await channel.send(
        content=f"<@&{ROLE_NOTIFICACION_RUTEOS}>",
        embed=embed,
        view=view
    )
    return str(msg.id), msg, view