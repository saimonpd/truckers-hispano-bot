import discord
from discord.ext import commands
from discord import app_commands
from services.route_services import route_create

import logging
log = logging.getLogger("route")

class Route(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="crear_ruteo", description="Crea un ruteo")
    @app_commands.choices(
        juego=[
            app_commands.Choice(name="Euro Truck Simulator 2", value="ets2"),
            app_commands.Choice(name="American Truck Simulator", value="ats")
        ],
        servidor=[
            app_commands.Choice(name="Servidor privado", value="servpriv"),
            app_commands.Choice(name="TruckersMP | Simulador 1", value="TMP/SIM1"),
            app_commands.Choice(name="TruckersMP | Simulador 2", value="TMP/SIM2"),
            app_commands.Choice(name="TruckersMP | Arcade", value="TMP/ARC"),
            app_commands.Choice(name="TruckersMP | Promods", value="PROMODS")
        ]
    )
    @app_commands.describe(
        fecha="DD/MM/YYYY",
        hora_reunion="HH:MM",
        hora_salida="HH:MM"
    )
    async def c_route_create(
        self,
        interaction: discord.Interaction,
        juego: app_commands.Choice[str],
        servidor: app_commands.Choice[str],
        fecha: str,
        hora_reunion: str,
        hora_salida: str,
        dlc: str = "No se requieren DCLs"
    ):

        try:
            await interaction.response.defer(ephemeral=True)

            data = {
                "game": juego.value,
                "server": servidor.value,
                "date": fecha,
                "meeting_date": hora_reunion,
                "departure_date": hora_salida,
                "required_dlc": dlc,
                "author_id": str(interaction.user.id),
                "guild_id": str(interaction.guild.id)
            }

            await route_create(interaction=interaction, channel=interaction.channel, data=data)
            await interaction.followup.send("✅ Ruta creada con éxito.")

        except ValueError as e:
            await interaction.followup.send(f"⚠️ {e}")

        except RuntimeError as e:
            log.error(f"Error creando ruta: {e}")
            await interaction.followup.send(f"❌ {e}")

async def setup(bot):
    await bot.add_cog(Route(bot))
            