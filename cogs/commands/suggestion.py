import discord
from discord.ext import commands
from discord import app_commands
from services.suggestion_services import suggestion_create, suggestion_resolve
from config.roles import ROLE_STAFF
from database.models.suggestion import SuggestionStatus

import logging 
log = logging.getLogger("suggestion")

class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="crear_sugerencia", description="Crea una sugerencia para el servidor")
    async def c_suggestion_create(
        self,
        interaction: discord.Interaction,
        sugerencia: str,
    ):
        await interaction.response.defer(ephemeral=True)

        data = {
            "description": sugerencia,
            "author_id": str(interaction.user.id),
            "guild_id": str(interaction.guild.id)
        }

        # Guardar la sugerencia en la base de datos y enviar un mensaje de confirmación al usuario.
        try:
            await suggestion_create(channel=interaction.channel, interaction=interaction, data=data)
            await interaction.followup.send(f"✅ Sugerencia creada con éxito.")

        except ValueError as e:
            await interaction.followup.send(f"⚠️ {e}")

        except RuntimeError as e:
            log.error(f"Error creando sugerencia: {e}")
            await interaction.followup.send(f"❌ {e}")

    @app_commands.command(name="resolver_sugerencia", description="[Solo administración] Resuelve una sugerencia existente")
    @app_commands.checks.has_role(ROLE_STAFF)
    @app_commands.describe(
        suggestion_id="ID de la sugerencia a resolver",
        resolution="Estado al que cambiará la sugerencia",
        respuesta="Explicación o respuesta del moderador a la sugerencia"
    )
    @app_commands.choices(
        resolution=[
            app_commands.Choice(name="En Revisión", value=SuggestionStatus.IN_REVISION.value),
            app_commands.Choice(name="Aceptada", value=SuggestionStatus.APPROVED.value),
            app_commands.Choice(name="Rechazada", value=SuggestionStatus.DENIED.value),
        ]
    )
    async def c_suggestion_resolve(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        resolution: app_commands.Choice[str],
        respuesta: str
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            resultado = await suggestion_resolve(
                bot=self.bot,
                suggestion_id=suggestion_id,
                new_status=resolution.value,
                moderator=interaction.user,
                moderator_answer=respuesta
            )
            await interaction.followup.send(f"✅ Sugerencia `#{suggestion_id}` actualizada a **{resolution.name}**.")
        except ValueError as ve:
            await interaction.followup.send(f"⚠️ {ve}")
        except Exception as e:
            log.error(f"Error al resolver sugerencia {suggestion_id}: {e}")
            await interaction.followup.send("❌ Ocurrió un error al procesar la resolución de la sugerencia.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestion(bot))