import discord
import asyncio
from discord.ext import commands
import os
from config import TOKEN

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()

        # Inicia el bot con su prefijo e intents
        # Starts the bot with its prefix and intents
        super().__init__(
            command_prefix = "!",
            intents = intents
        )

    async def setup_hook(self):
        # Usamos setup_hook y no on_ready porque: 
        # - nos permite cargar cogs de manera segura
        # - registrar vistas antes de que el bot este online evitando errores de sincronizacion
        # - es un metodo recomendado por discord.py para inicializacion asincrona
        # Why we use setup_hook and not on_ready:
        # - allows us to load cogs in a safe manner
        # - registers views before going online, is more secure.
        # - is a recommended method by discord.py to use async init

        print("Loading cogs...")

        # aqui iran las views
        # here is going to be the views

        # Carga automaticamente todos los /cogs que tenemos 
        # Automatically loads all the /cogs that we have
        for root, dirs, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    path = os.path.join(root, file)

                    # Adaptamos el texto para mostrarlo
                    # We adapt the path string for module loading
                    cog = path.replace("\\", ".").replace("/", ".")[:-3]

                    try:
                        await self.load_extension(cog)
                        print(f"{cog} loaded")
                    except Exception as e:
                        print(f"Error in {cog}: {e}")

        # Sincronizamos los slash commands con Discord.
        # Nota: Cuando se añade un nuevo slash el cliente debe de reiniciar la app para que le aparezca, no es problema nuestro.
        # We sync the slash commands on Discord
        # Note: When we add a new slash command the user needs to restart the app to see it, this is expected Discord behavior.
        await self.tree.sync()
        print(f"Slash commands synced")

    async def on_ready(self):
        print(f"Bot connected: {self.user}")

bot = MyBot()
asyncio.run(bot.start(TOKEN))