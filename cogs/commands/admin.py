import discord
from discord.ext import commands
from discord import app_commands
from utils.dm_utils import send_dm
from services import moderation_services as mod 
from utils.safe_send import safe_send

import logging
log = logging.getLogger("commands")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_kick", description="[Solo administradores] Expulsa a un usuario")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(
        usuario="Usuario",
        razon="Razón"
    )
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        """Expulsa un usuario del servidor"""

        try: 
            await mod.kick(usuario, interaction.user, razon)
            log.info(f"KICK | {interaction.user} expulsó a {usuario} | Razón: {razon}")
            await safe_send(interaction, f"{usuario} fue expulsado.")

        except discord.Forbidden:
            log.warning(f"KICK | Sin permisos | Ejecutado por {interaction.user}")
            await safe_send(interaction, "No tengo permitido expulsar")

        except discord.HTTPException as e:
            log.error(f"KICK | Error de red o Discord con {usuario}: {e}")
            await safe_send(interaction, "Ocurrió un error al intentar expulsar al usuario, prueba mas tarde.")

        except Exception as e:
            log.error(f"Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, intentalo de nuevo o ponte en contacto con los administradores.")

        return

    @app_commands.command(name="admin_ban", description="[Solo administradores] Banea a un usuario")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(
        usuario="Usuario",
        razon="Razón"
    )
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str):
        """Banea a un usuario del servidor"""

        try:
            await mod.ban(usuario, interaction.user, razon)
            log.info(f"BAN | {interaction.user} baneó a {usuario} | Razón: {razon}")
            await safe_send(interaction, f"{usuario} fue baneado.")

        except discord.Forbidden:
            log.warning(f"BAN | Sin permisos | Ejecutado por: {interaction.user}")
            await safe_send(interaction, "No tengo permitido banearlo.")

        except discord.HTTPException as e:
            log.error(f"BAN | Error de red o Discord con {usuario}: {e}")
            await safe_send(interaction, "Ocurrió un error al intentar banear al usuario, prueba mas tarde.")

        except Exception as e:
            log.error(f"Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, intentalo de nuevo o ponte en contacto con los administradores.")


    @app_commands.command(name="admin_aislar", description="[Solo administradores] Aisla temporalmente a un usuario")
    @app_commands.checks.has_permissions(mute_members=True)
    @app_commands.describe(
        usuario="Usuario",
        razon="Razón",
        minutos="Minutos"
    )
    async def timeout(self, interaction: discord.Interaction, usuario: discord.Member, razon: str, minutos: int):
        """Aisla temporalmente a un usuario del servidor"""

        try:
            await mod.timeout(usuario, interaction.user, razon, minutos)
            log.info(f"TIMEOUT | {interaction.user} aislo durante {minutos} min a {usuario} | Razon: {razon}")
            await safe_send(interaction, f"{usuario} fue aislado")

        except discord.Forbidden:
            log.warning(f"TIMEOUT | Sin permisos | Ejecutado por: {interaction.user}")
            await safe_send(interaction, "No tengo permitido aislarle.")

        except discord.HTTPException as e:
            log.error(f"TIMEOUT | Error de red o Discord con {usuario}: {e}")
            await safe_send(interaction, "Ocurrió un error al intentar aislar al usuario, prueba mas tarde.")

        except Exception as e:
            log.error(f"Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, intentalo de nuevo o ponte en contacto con los administradores.")

    @app_commands.command(name="admin_editarnombre", description="[Solo administradores] Edita el nombre de un usuario")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    @app_commands.describe(
        usuario="Usuario",
        nuevo_nombre="Nuevo nombre",
        razon = "Razón"
    )
    async def change_nickname(self, interaction: discord.Interaction, usuario: discord.Member, nuevo_nombre: str, razon: str):
        """Cambia el nombre de un usuario dentro del servidor"""

        await interaction.response.defer(ephemeral=False)

        antiguo_nombre = usuario.name

        try:
            await mod.change_nickname(usuario, interaction, nuevo_nombre, razon)
            await safe_send(interaction, f"Nickname de {usuario.mention} cambiado")
            log.info(f"NICKNAME | Se ha cambiado el nombre de {interaction.user}, antes: {antiguo_nombre}  | Razón: {razon}")

            try:
                await send_dm(
                    usuario,
                    "Nombre cambiado",
                    f"Nuevo: {usuario}\nRazón: {razon}"
                )
            except discord.Forbidden:
                log.warning(f"NICKNAME | No se pudo enviar MD a {usuario} (MD deshabilitado)")
            except Exception as e:
                log.error(f"NICKNAME | Error al enviar MD a {usuario}: {e}")

        except discord.Forbidden:
            log.warning(f"NICKNAME | Sin permisos | Ejecutado por: {interaction.user}")
            await safe_send(interaction, "No tengo permisos para cambiar el nombre")

        except discord.HTTPException as e:
            log.error(f"NICKNAME | Error de red o Discord con {usuario}: {e}")
            await safe_send(interaction, "Ocurrió un error al intentar cambiar el nombre al usuario, prueba mas tarde.")

        except Exception as e:
            log.error(f"Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, intentalo de nuevo o ponte en contacto con los administradores.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
