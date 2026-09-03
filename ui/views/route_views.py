import discord
import asyncio
import logging
from config.roles import ROLE_NOTIFICACION_RUTEOS
from config.channels import VOICE_CHANNEL_EVENT_ETS2, VOICE_CHANNEL_EVENT_ATS
from utils.safe_send import safe_send
from services.route_services import route_join, route_leave
from services.route_services import route_join, route_leave

log = logging.getLogger("route")

_locks: dict[str, asyncio.Lock] = {}

class RouteView(discord.ui.View):
    def __init__(self, data: dict | None = None):
        super().__init__(timeout=None)

        self.data = data or {}
        self.game = self.data.get("game")
        self.route_id = None

    @discord.ui.button(
        label="Apuntarme",
        style=discord.ButtonStyle.success,
        custom_id="route_join_btn",
        row=0
    )

    async def join_route(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.route_id is None:
            await safe_send(interaction, "❌ No se pudo identificar el ruteo.")
            return

        lock = _locks.setdefault(str(self.route_id), asyncio.Lock())

        async with lock:
            updated_embed = await route_join(self.route_id, interaction.user.id)
            await interaction.message.edit(embed=updated_embed)
            await safe_send(interaction, "✅ Te has apuntado al ruteo.")

    @discord.ui.button(
        label="Desapuntarme",
        style=discord.ButtonStyle.danger,
        custom_id="route_leave_btn",
        row=0
    )

    async def leave_route(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.route_id is None:
            await safe_send(interaction, "❌ No se pudo identificar el ruteo.")
            return

        lock = _locks.setdefault(str(self.route_id), asyncio.Lock())

        async with lock:
            updated_embed = await route_leave(self.route_id, interaction.user.id)
            await interaction.message.edit(embed=updated_embed)
            await safe_send(interaction, "✅ Te has desapuntado del ruteo.")

    @discord.ui.button(
        label="🔊 Canal de voz",
        style=discord.ButtonStyle.primary,
        custom_id="route_voice_channel_btn",
        row=0
    )

    async def join_voice_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = VOICE_CHANNEL_EVENT_ETS2 if self.game == "ets2" else VOICE_CHANNEL_EVENT_ATS
        await safe_send(interaction, url)
        
    @discord.ui.button(
        label="🔔 Avisos Ruteos",
        style=discord.ButtonStyle.secondary,
        custom_id="route_toggle_role_btn",
        row=0
    )

    async def toggle_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        rol = interaction.guild.get_role(ROLE_NOTIFICACION_RUTEOS)

        if not rol:
            return await safe_send(interaction, "❌ El rol de avisos no está configurado correctamente.")

        member = interaction.user
        if rol in member.roles:
            await member.remove_roles(rol)
            await safe_send(interaction, "🔕 Ya no recibirás menciones de ruteos.")
        else:
            await member.add_roles(rol)
            await safe_send(interaction, "🔔 Recibirás avisos de los próximos ruteos.")