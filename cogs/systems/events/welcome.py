import discord
from discord.ext import commands
import logging
from services.welcome_services import WelcomeService

log = logging.getLogger("welcome")

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.service = WelcomeService(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.service.handle_new_member(member)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
                
        