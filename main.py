import discord
import asyncio
from discord.ext import commands
import os
from config.config import TOKEN
from ui.views.welcome_views import WelcomeView

class MyBot(commands.Bot):
    def __init__(self):
        # Inicia el bot con su prefijo e intents
        intents = discord.Intents.default()
        intents.members = True
        
        super().__init__(
            command_prefix = "!",
            intents = intents
        )

    async def setup_hook(self):
        # Usamos setup_hook y no on_ready porque: 
        # - nos permite cargar cogs de manera segura
        # - registrar vistas antes de que el bot este online evitando errores de sincronizacion
        # - es un metodo recomendado por discord.py para inicializacion asincrona

        print("Loading cogs...")

        # aqui iran las views
        self.add_view(WelcomeView())

        # Carga automaticamente todos los /cogs que tenemos 
        for root, dirs, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    path = os.path.join(root, file)

                    # Adaptamos el texto para mostrarlo
                    cog = path.replace("\\", ".").replace("/", ".")[:-3]

                    try:
                        await self.load_extension(cog)
                        print(f"{cog} loaded")
                    except Exception as e:
                        print(f"Error in {cog}: {e}")

        # Sincronizamos los slash commands con Discord.
        # Nota: Cuando se añade un nuevo slash el cliente debe de reiniciar la app para que le aparezca, no es problema nuestro.
        await self.tree.sync()
        print(f"Slash commands synced")

    async def on_ready(self):
        print(f"Bot connected: {self.user}")

bot = MyBot()
asyncio.run(bot.start(TOKEN))