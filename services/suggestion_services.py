from database.repositories.suggestion_repository import update_suggestion_status
from discord import guild
from database.models.suggestion import SuggestionStatus
from database.repositories.suggestion_repository import get_suggestion_by_id
import discord
import logging
from discord import channel
from database.repositories.suggestion_repository import suggestion_save
from ui.embeds.suggestion_builders import build_suggestion_embed

async def suggestion_create(channel: discord.TextChannel, data: dict) -> dict:
    if discord.utils.get(channel.guild.channels, name=data["title"]):
        raise ValueError(f"Ya existe una sugerencia con el título '{data['title']}'.")

    try:
        data["id_user"] = str(data["author_id"])
        data["title"] = data["title"]
        data["description"] = data["description"]

        message_id = await _publish_on_discord(guild, data)
        data["id_message"] = message_id

        # Llamada al repositorio para guardar la sugerencia en la base de datos
        suggestion = suggestion_save(data)
        if not suggestion:
            raise RuntimeError("No se pudo guardar la sugerencia en la base de datos.")

        return suggestion

    except Exception as e:
        logging.error(f"Error creando sugerencia '{data['title']}': {e}")
        raise RuntimeError("Hubo un error al crear la sugerencia.")

async def suggestion_resolve(
    bot: discord.Client,
    suggestion_id: int,
    new_status: str,
    moderator: discord.Member | discord.User,
    moderator_answer: str
) -> bool:
    # Comprobar si existe la sugerencia
    suggestion = get_suggestion_by_id(suggestion_id)
    if not suggestion:
        raise ValueError(f"No se encontró ninguna sugerencia con el ID `#{suggestion_id}`.")

    # Comprobar que el estado sea 'Pendiente'
    current_status = suggestion.get("status")
    if current_status != SuggestionStatus.PENDING.value:
        raise ValueError(
            f"La sugerencia `#{suggestion_id}` no se puede resolver porque ya tiene el estado **'{current_status}'**."
        )
    # Actualizar en Base de Datos
    updated = update_suggestion_status(
        suggestion_id=suggestion_id,
        status=new_status,
        moderator_id=moderator.id,
        moderator_name=moderator.display_name,
        moderator_answer=moderator_answer
    )
    if not updated:
        raise RuntimeError("No se pudo actualizar el estado en la base de datos.")

    # Actualizar el embed en Discord si existe el mensaje
    try:
        suggestion["status"] = new_status
        suggestion["moderator_name"] = moderator.display_name
        suggestion["moderator_answer"] = moderator_answer

        if suggestion.get("id_message"):
            await _publish_on_discord(guild, suggestion)
            
    except Exception as e:
        logging.warning(f"No se pudo editar el mensaje de Discord de la sugerencia #{suggestion_id}: {e}")
    return True


async def _publish_on_discord(data: dict) -> str:
    from ui.views.suggestion_views import SuggestionView

    # Crea el embed y el view para la sugerencia
    embed = build_suggestion_embed(data)
    view = SuggestionView()

    msg = await channel.send(
        embed=embed,
        view=view
    )

    return str(msg.id)

