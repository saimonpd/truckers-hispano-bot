import discord
import asyncio
import logging
from config.roles import ROLE_NOTIFICACION_EVENTOS
from services.events_services import toggle_participacion
from utils.safe_send import safe_send

log = logging.getLogger("events")

# Un lock por evento (message_id), no uno global compartido por todos los
# eventos. Evita que apuntarse a un convoy bloquee a quien se apunta a otro.
_locks: dict[str, asyncio.Lock] = {}


def _get_lock(message_id: str) -> asyncio.Lock:
    return _locks.setdefault(message_id, asyncio.Lock())


class EventView(discord.ui.View):
    def __init__(self, link_trucksbook: str = None, link_truckersmp: str = None):
        super().__init__(timeout=None)

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
            return await safe_send(interaction, "❌ El rol de avisos no está configurado correctamente.")

        member = interaction.user
        if rol in member.roles:
            await member.remove_roles(rol)
            await safe_send(interaction, "🔕 Ya no recibirás menciones de eventos.")
        else:
            await member.add_roles(rol)
            await safe_send(interaction, "🔔 Recibirás avisos en los próximos eventos.")

    @discord.ui.button(
        label="✅ Apuntarse / Desapuntarse",
        style=discord.ButtonStyle.success,
        custom_id="event_join_toggle_btn",
        row=1
    )
    async def join_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = str(interaction.message.id)

        async with _get_lock(message_id):
            try:
                await interaction.response.defer(ephemeral=True)
            except (discord.errors.InteractionResponded, discord.errors.NotFound):
                return

            try:
                texto_respuesta, nuevo_embed = await toggle_participacion(
                    message_id=message_id,
                    discord_id=interaction.user.id,
                    nombre=interaction.user.display_name,
                )
            except ValueError as e:
                return await safe_send(interaction, f"❌ {e}")
            except RuntimeError as e:
                log.error(f"Error al modificar participante en evento {message_id}: {e}")
                return await safe_send(
                    interaction,
                    "❌ Ha ocurrido un error al procesar tu solicitud. Inténtalo de nuevo más tarde "
                    "o contacta con un administrador si el problema persiste."
                )

            try:
                await interaction.message.edit(embed=nuevo_embed, view=self)
                await interaction.followup.send(texto_respuesta, ephemeral=True)
            except Exception as e:
                log.error(f"Error al editar mensaje de evento {message_id}: {e}")
                await safe_send(
                    interaction,
                    "⚠️ Tu estado se guardó, pero hubo un error visual al actualizar el mensaje. "
                    "Se corregirá con la próxima interacción."
                )