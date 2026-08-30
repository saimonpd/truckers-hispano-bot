import logging
import discord
from discord.ext import commands
from discord import app_commands
from config.roles import ROLE_ENCARGADO_EMPRESAS
from services.company_services import crear_empresa, eliminar_empresa

import logging
log = logging.getLogger("company")

class Company(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="registrar_empresa", description="[Solo encargado] Registrar una empresa")
    @app_commands.checks.has_role(ROLE_ENCARGADO_EMPRESAS)
    async def registrar_empresa(
        self,
        interaction: discord.Interaction,
        nombre_empresa: str,
        dueño_empresa: discord.Member
    ):
        await interaction.response.defer(ephemeral=True)

        data = {
            "dueño_empresa": str(dueño_empresa.id),
            "nombre_empresa": nombre_empresa
        }

        try:
            await crear_empresa(guild=interaction.guild, data=data)
            await interaction.followup.send(f"✅ Empresa **{nombre_empresa}** registrada con éxito.")
        except ValueError as e:
            await interaction.followup.send(f"⚠️ {e}")
        except RuntimeError as e:
            logging.error(f"Error registrando empresa '{nombre_empresa}': {e}")
            await interaction.followup.send(f"❌ {e}")

    @app_commands.command(name="eliminar_empresa", description="[Solo encargado] Elimina una empresa")
    @app_commands.describe(rol_empresa="Menciona a la empresa a elminar")
    @app_commands.checks.has_role(ROLE_ENCARGADO_EMPRESAS)
    async def eliminar_empresa_cmd(
        self, 
        interaction: discord.Interaction, 
        rol_empresa: discord.Role):

        await interaction.response.defer(ephemeral=True)

        try:
            await eliminar_empresa(interaction.guild, str(rol_empresa.id), interaction.channel)
            await interaction.followup.send(f"✅ La empresa **{rol_empresa.name}** ha sido eliminada.")
        except ValueError as e:
            await interaction.followup.send(f"⚠️ {e}")
        except RuntimeError as e:
            logging.error(f"Error eliminando empresa: {e}")
            await interaction.followup.send(f"❌ {e}")
        except discord.NotFound:
            logging.warning(
                f"No se pudo enviar confirmación de borrado para '{rol_empresa.name}' "
                "(probablemente se ejecutó desde el canal que se acaba de eliminar)."
            )

async def setup(bot):
    await bot.add_cog(Company(bot))