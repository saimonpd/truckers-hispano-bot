from database.repositories.suggestion_repository import (
    get_suggestion_by_id,
    suggestion_save,
    update_suggestion_status,
)
from database.models.suggestion import SuggestionStatus
import discord
import logging
from ui.embeds.suggestion_builders import build_suggestion_embed

log = logging.getLogger("suggestions")


async def suggestion_create(channel: discord.TextChannel, data: dict) -> dict:
    if discord.utils.get(channel.guild.channels, name=data["title"]):
        raise ValueError(f"Ya existe una sugerencia con el título '{data['title']}'.")

    try:
        data["id_user"] = str(data["author_id"])
        data["title"] = data["title"]
        data["description"] = data["description"]
        data["id_channel"] = str(channel.id)

        message_id, msg = await _publish_on_discord(channel, data)
        data["id_message"] = message_id

        # Llamada al repositorio para guardar la sugerencia en la base de datos
        suggestion = suggestion_save(data)
        if not suggestion:
            try:
                await msg.delete()
            except Exception:
                pass
            raise RuntimeError("No se pudo guardar la sugerencia en la base de datos.")

        # Actualizar el embed para mostrar el ID de sugerencia asignado por la BD
        try:
            await msg.edit(embed=build_suggestion_embed(suggestion))
        except Exception as e:
            log.warning(f"No se pudo actualizar el ID en el embed de la sugerencia #{suggestion.get('suggestion_id')}: {e}")

        return suggestion

    except ValueError:
        raise
    except Exception as e:
        log.error(f"Error creando sugerencia '{data.get('title')}': {e}")
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
        moderator_id=str(moderator.id),
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

        channel_id = suggestion.get("id_channel")
        message_id = suggestion.get("id_message")

        if channel_id and message_id:
            target_channel = bot.get_channel(int(channel_id))
            if not target_channel:
                target_channel = await bot.fetch_channel(int(channel_id))

            if target_channel:
                msg = await target_channel.fetch_message(int(message_id))
                await msg.edit(embed=build_suggestion_embed(suggestion))

    except Exception as e:
        log.warning(f"No se pudo editar el mensaje de Discord de la sugerencia #{suggestion_id}: {e}")

    return True


async def _publish_on_discord(channel: discord.TextChannel, data: dict) -> tuple[str, discord.Message]:
    from ui.views.suggestion_views import SuggestionView

    # Crea el embed y el view para la sugerencia
    embed = build_suggestion_embed(data)
    view = SuggestionView()

    msg = await channel.send(
        embed=embed,
        view=view
    )

    return str(msg.id), msg