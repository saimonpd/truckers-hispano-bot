import discord
from discord.ext import commands
from discord import app_commands
from config.roles import ROLE_STAFF
from utils.safe_send import safe_send
from services.sanction_services import sanction_register, sanction_delete, sanction_list

import logging
log = logging.Logger("sanctions")

class Sanctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sancionar", description="[Administracion] Añade una sancion a un usuario")
    @app_commands.checks.has_role(ROLE_STAFF)
    async def c_sancion_register(
            self,
            interaction: discord.Interaction,
            usuario: discord.Member,
            razon: str
    ):
        try:
            await interaction.response.defer(ephemeral=True)

            data = {
                "mod": interaction.user.id,
                "usuario": usuario.id,
                "razon": razon
            }

            result = await sanction_register(bot=self.bot, data=data)
            await safe_send(interaction, result)

        except Exception as e:
            log.error (f"SANCTION | Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, contacta con un administrador")


    @app_commands.command(name="eliminar_sancion", description="[Administracion] Elimina una sancion a un usuario")
    @app_commands.checks.has_role(ROLE_STAFF)
    async def c_sanction_delete(
            self,
            interaction: discord.Interaction,
            id: int
    ):
        try:
            await interaction.response.defer(ephemeral=True)

            data = {
                "mod": interaction.user.id,
                "id_sancion": id
            }

            result = await sanction_delete(bot=self.bot, data=data)

            if isinstance(result, dict):
                await interaction.followup.send(embed=result["embed"], view=result["view"], ephemeral=True)
            else: 
                await safe_send(interaction, result)

        except Exception as e:
            log.error(f"SANCTION | Error en comando {interaction.command.name}: {e}")

    @app_commands.command(name="ver_sanciones", description="[Administracion] Ver las sanciones de un usuario")
    @app_commands.checks.has_role(ROLE_STAFF)
    async def c_sanction_list(
            self,
            interaction: discord.Interaction,
            usuario: discord.User
    ):
        try:
            await interaction.response.defer(ephemeral=True)

            data = {
                "mod": interaction.user.id,
                "usuario": usuario.id
            }

            result = await sanction_list(bot=self.bot, data=data)

            if isinstance(result, dict):
                await interaction.followup.send(embed=result["embed"], ephemeral=True)
            else:
                await safe_send(interaction, result)

        except Exception as e:
            log.error(f"SANCTION | Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, contacta con un administrador")


async def setup(bot):
    await bot.add_cog(Sanctions(bot))
            