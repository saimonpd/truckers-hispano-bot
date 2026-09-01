from database.repositories.suggestion_repository import (
    get_suggestion_by_id,
    suggestion_save,
    update_suggestion_status,
)
from database.repositories.vote_repository import save_or_update_vote
from database.models.suggestion import SuggestionStatus
import discord
import logging
from ui.embeds.suggestion_builders import build_suggestion_embed

log = logging.getLogger("suggestion")


async def suggestion_create(channel: discord.TextChannel, data: dict) -> dict:
    try:
        data["id_user"] = str(data["author_id"])
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
        log.error(f"Error creando sugerencia: {e}")
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
                from ui.views.suggestion_views import SuggestionView
                msg = await target_channel.fetch_message(int(message_id))
                disabled_view = SuggestionView(suggestion_id=suggestion_id, disabled=True)
                await msg.edit(embed=build_suggestion_embed(suggestion), view=disabled_view)

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

async def process_suggestion_vote(suggestion_id: int, user_id: str, vote_type: str) -> tuple[str, discord.Embed]:
    """
    Registra el voto de un usuario en la tabla suggestion_vote (database/models/vote.py)
    y devuelve el texto de confirmación junto con el Embed actualizado.
    """
    # Comprobar que la sugerencia exista y no esté resuelta
    suggestion = get_suggestion_by_id(suggestion_id)
    if not suggestion:
        raise ValueError(f"No se encontró la sugerencia con ID `#{suggestion_id}`.")

    if suggestion.get("status") != SuggestionStatus.PENDING.value:
        raise ValueError(f"Esta sugerencia ya está finalizada con estado **'{suggestion.get('status')}'**.")

    # Registrar el voto en BD
    exito = save_or_update_vote(suggestion_id=suggestion_id, user_id=user_id, vote_type=vote_type)
    if not exito:
        raise RuntimeError("No se pudo registrar el voto en la base de datos.")

    # Obtener la sugerencia actualizada con los nuevos votos
    suggestion_actualizada = get_suggestion_by_id(suggestion_id)
    if not suggestion_actualizada:
        suggestion_actualizada = suggestion

    tipo_txt = "positivo" if vote_type == "positive" else "negativo"
    texto_respuesta = f"✅ Has registrado tu voto **{tipo_txt}** en la sugerencia."
    nuevo_embed = build_suggestion_embed(suggestion_actualizada)

    return texto_respuesta, nuevo_embed