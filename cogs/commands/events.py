import discord
from discord.ext import commands
from discord import app_commands
from config.roles import ENCARGADO_EVENTOS
from services.events_services import create_event
from utils.safe_send import safe_send

import logging 
log = logging.getLogger("events")

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="crear_evento", description="[Solo encargado] Crea un evento dentro del servidor")
    @app_commands.checks.has_role(ENCARGADO_EVENTOS)
    @app_commands.describe(
        fecha = "DD/MM/YYYY",
        hora_reunion = "HH:MM",
        hora_salida = "HH:MM"
    )
    @app_commands.choices(
        juego=[
            app_commands.Choice(name="Euro Truck Simulator 2", value="ets2"),
            app_commands.Choice(name="American Truck Simulator", value="ats")
        ],
        servidor=[
            app_commands.Choice(name="Servidor privado", value="servpriv"),
            app_commands.Choice(name="TruckersMP | Simulador 1", value="TMP/SIM1"),
            app_commands.Choice(name="TruckersMP | Simulador 2", value="TMP/SIM2"),
            app_commands.Choice(name="TruckersMP | Arcade", value="TMP/ARC")
        ]
        )
    async def newevent(
        self,
        # Obligatorios
        interaction: discord.Interaction,
        titulo: str,
        descripcion: str,
        juego: app_commands.Choice[str],
        servidor: app_commands.Choice[str],
        organizador: str,
        fecha: str,
        hora_reunion: str,
        hora_salida: str,
        ruta_origen: str,
        ruta_destino: str,

        # Opcionales
        link_trucksbook: str = None,
        link_truckersmp: str = None,
        parada_intermedio: str = "No hay parada intermedia.",
        dlcs_requeridos: str = "No se requieren DLCS",
        carga: str = "Libre",
        trailer: str = "Libre",
        ruta_imagen: str = None
    ):

        try:
            await interaction.response.defer(ephemeral=True)

            event_data = {
                "creador_id": str(interaction.user.id),
                "titulo": titulo,
                "descripcion": descripcion,
                "juego_name": juego.name,
                "juego_value": juego.value,
                "servidor_name": servidor.name,
                "servidor_value": servidor.value,
                "organizador": organizador,
                "fecha": fecha,
                "hora_reunion": hora_reunion,
                "hora_salida": hora_salida,
                "ruta_origen": ruta_origen,
                "ruta_destino": ruta_destino,
                "link_trucksbook": link_trucksbook,
                "link_truckersmp": link_truckersmp,
                "parada_intermedio": parada_intermedio,
                "dlcs_requeridos": dlcs_requeridos,
                "carga": carga,
                "trailer": trailer,
                "ruta_imagen": ruta_imagen
            }

            result = await create_event(bot=self.bot, data=event_data)
            await safe_send(interaction, result)

        except ValueError as ve:
            # Captura errores de validacion ( fecha mal escrita )
            await safe_send(interaction, f"Error de validación: {ve}")

        except Exception as e:
            log.error(f"EVENTS | Error en comando {interaction.command.name}: {e}")
            await safe_send(interaction, "Algo ha salido mal, contacta con un administrador.")

async def setup(bot):
    await bot.add_cog(Events(bot))