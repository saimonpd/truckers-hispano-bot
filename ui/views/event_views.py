import discord
import asyncio
import logging
from config.roles import ROLE_NOTIFICACION_EVENTOS
from ui.embeds.event_builders import build_event_embed

# Importa tus funciones de repositorio
from database.repositories.event_repository import (
    obtener_datos_evento,
    obtener_lista_ids_evento,
    modificar_participantes_evento
)

log = logging.getLogger("events")

class EventView(discord.ui.View):
    def __init__(self, link_trucksbook: str = None, link_truckersmp: str = None):
        super().__init__(timeout=None)
        self.lock = asyncio.Lock()

        if link_trucksbook:
            self.add_item(discord.ui.Button(
                label="TrucksBook",
                style=discord.ButtonStyle.link,
                url=link_trucksbook,
                row=0
            ))

        if link_truckersmp:
            self.add_item(discord.ui.Button(
                label="TruckersMP",
                style=discord.ButtonStyle.link,
                url=link_truckersmp,
                row=0
            ))

    @discord.ui.button(
        label="🔔 Avisos Eventos", 
        style=discord.ButtonStyle.primary, 
        custom_id="event_toggle_role_btn", 
        row=1
    )
    async def toggle_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol = interaction.guild.get_role(ROLE_NOTIFICACION_EVENTOS)

        if not rol:
            return await interaction.response.send_message("❌ El rol de avisos no está configurado correctamente.", ephemeral=True)

        member = interaction.user
        if rol in member.roles:
            await member.remove_roles(rol)
            await interaction.response.send_message("🔕 Ya no recibirás menciones de eventos.", ephemeral=True)
        else:
            await member.add_roles(rol)
            await interaction.response.send_message("🔔 ¡Perfecto! Recibirás avisos en los próximos eventos.", ephemeral=True)

    @discord.ui.button(
        label="✅ Apuntarse / Desapuntarse", 
        style=discord.ButtonStyle.success, 
        custom_id="event_join_toggle_btn", 
        row=1
    )
    async def join_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = str(interaction.message.id)

        async with self.lock:
            # 1. Defer para evitar timeout de 3 segundos de Discord
            try:
                await interaction.response.defer(ephemeral=True)
            except (discord.errors.InteractionResponded, discord.errors.NotFound):
                return

            # 2. Obtener datos actuales del evento desde la BD
            data = obtener_datos_evento(message_id)
            if not data:
                return await interaction.followup.send("❌ No se encontró la información del evento en la base de datos.", ephemeral=True)

            participantes = obtener_lista_ids_evento(message_id)

            # 3. Lógica de Toggle (Unirse/Salir)
            if interaction.user.id in participantes:
                accion = "salirse"
                texto_respuesta = "❌ Te has desapuntado del evento."
            else:
                accion = "unirse"
                texto_respuesta = "✅ ¡Te has inscrito con éxito al evento!"

            exito = modificar_participantes_evento(
                message_id=message_id,
                discord_id=str(interaction.user.id),
                nombre=interaction.user.display_name,
                accion=accion
            )

            if not exito:
                return await interaction.followup.send("❌ Error al guardar tu estado en la base de datos.", ephemeral=True)

            # 4. Actualizar lista de participantes y reconstruir Embed
            data["participantes"] = obtener_lista_ids_evento(message_id)
            new_embed = build_event_embed(data)

            # 5. Editar el mensaje original con el Embed actualizado
            try:
                await interaction.message.edit(embed=new_embed, view=self)
                await interaction.followup.send(texto_respuesta, ephemeral=True)
            except Exception as e:
                log.error(f"Error al editar mensaje de evento {message_id}: {e}")