import discord
import logging
log = logging.getLogger("safe_send")

async def safe_send(
    interaction: discord.Interaction,
    message: str,
    ephemeral: bool = True
):
    try:
        if interaction.response.is_done():
            return await interaction.followup.send(
                message,
                ephemeral=ephemeral
            )
        else:
            return await interaction.response.send_message(
                message,
                ephemeral=ephemeral
            )

    except discord.NotFound:
        # Interaction expiró (si tarda >3s o Discord la invalida)
        log.warning("SAFE SEND | La interaccion expiró")
        return None

    except discord.HTTPException as e:
        # Errores de Discord API
        log.error(f"SAFE SEND | Eror en la API Discord: {e}")
        return None

    except Exception as e:
        # Cualquier error inesperado
        log.error(f"SAFE SEND | Error inesperado: {e}")
        return None