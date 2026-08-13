import discord
from discord.ext import commands
from ui.embeds.welcome_builders import build_welcome_embed
from ui.views.welcome_views import WelcomeView
import logging
from config.channels import CHANNEL_WELCOME
from config.roles import AUTO_ROLE_ID

log = logging.getLogger("welcome")

class WelcomeService:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def handle_new_member(self, member: discord.Member) -> None:
        await self._assign_role(member, AUTO_ROLE_ID)
        await self._send_welcome_message(member)

    async def _assign_role(self, member: discord.Member, role_id: int) -> bool:
        role = member.guild.get_role(role_id)
        if role is None:
            log.error(f"WELCOME | Role {role_id} not found")
            return False
        try:
            await member.add_roles(role, reason="Automatic welcome")
            log.info(f"WELCOME | Role assigned to {member.name}")
            return True
        except discord.Forbidden:
            log.error(f"WELCOME | Missing permissions to assign '{role.name}'")
            return False

    async def _send_welcome_message(self, member: discord.Member) -> None:
        channel = self.bot.get_channel(CHANNEL_WELCOME)
        if channel is None:
            log.error(f"WELCOME | Channel {CHANNEL_WELCOME} not found")
            return
        try:
            await channel.send(
                content=member.mention,
                embed=build_welcome_embed(member),
                view=WelcomeView(),
            )
        except discord.Forbidden:
            log.error(f"WELCOME | Missing permissions to send message in {channel}")