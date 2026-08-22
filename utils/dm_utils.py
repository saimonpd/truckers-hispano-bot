import discord
import logging

log = logging.getLogger("dm_utils")


async def send_dm(user: discord.Member, title: str, description: str) -> bool:
    try:
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red()
        )
        await user.send(embed=embed)
        log.info(f"DM enviado a {user} ({user.id}) — asunto: {title}")
        return True

    except discord.Forbidden:
        # Usuario bloquea al bot o tiene los MD cerrados.
        log.warning(f"No se pudo enviar DM a {user} ({user.id}): MDs cerrados o bot bloqueado")
        return False

    except discord.HTTPException as e:
        log.error(f"Error de la API de Discord al enviar DM a {user} ({user.id}): {e}")
        return False

    except Exception as e:
        log.error(f"Error inesperado al enviar DM a {user} ({user.id}): {e}")
        return False