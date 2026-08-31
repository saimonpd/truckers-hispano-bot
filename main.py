import discord
import asyncio
import logging
from discord.ext import commands
import os
from config.config import TOKEN
from ui.views.welcome_views import WelcomeView
from ui.views.event_views import EventView
from ui.views.suggestion_views import SuggestionView
from database.connection import init_pool
from utils.startup_checks import run_startup_checks

log = logging.getLogger("main")


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
        # Inicia las pools en BD
        init_pool()

        # Usamos setup_hook y no on_ready porque: 
        # - nos permite cargar cogs de manera segura
        # - registrar vistas antes de que el bot este online evitando errores de sincronizacion
        # - es un metodo recomendado por discord.py para inicializacion asincrona

        print("Loading cogs...")

        # aqui iran las views
        self.add_view(WelcomeView())
        self.add_view(EventView())
        self.add_view(SuggestionView())

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
        # Las comprobaciones de arranque se ejecutan aqui y no en setup_hook porque
        # necesitan que el cache de guilds/canales del bot ya este poblado
        # (bot.guilds esta vacio durante setup_hook, antes de conectar al gateway).
        todo_ok = await run_startup_checks(self)
 
        if todo_ok:
            log.info(f"Bot connected: {self.user} — todas las comprobaciones de arranque pasaron correctamente")
        else:
            log.warning(
                f"Bot connected: {self.user} — el bot esta online pero una o mas comprobaciones "
                "de arranque fallaron (ver log de arriba). Revisa la configuracion antes de dar el "
                "servicio por operativo."
            )

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
 
    bot = MyBot()
    try:
        asyncio.run(bot.start(TOKEN))
    except KeyboardInterrupt:
        log.info("Bot detenido manualmente (KeyboardInterrupt)")
 
 
if __name__ == "__main__":
    main()