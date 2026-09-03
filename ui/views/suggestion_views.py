import re
import logging
import discord
from services.suggestion_services import process_suggestion_vote
from utils.safe_send import safe_send

log = logging.getLogger("suggestion")


class SuggestionView(discord.ui.View):
    def __init__(self, suggestion_id: int | None = None, disabled: bool = False):
        super().__init__(timeout=None)
        self.suggestion_id = suggestion_id

        if disabled:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True

    # Funcion encargada de identificar el ID de la sugerencia para asignarle el voto
    def _extract_suggestion_id(self, message: discord.Message | None) -> int | None:
        if self.suggestion_id is not None:
            return self.suggestion_id

        if not message or not message.embeds:
            return None

        embed = message.embeds[0]
        if embed.footer and embed.footer.text:
            match = re.search(r"ID:\s*(\d+)", embed.footer.text) or re.search(r"ID de Sugerencia:\s*(\d+)", embed.footer.text) or re.search(r"(\d+)", embed.footer.text)
            if match:
                return int(match.group(1))

        for field in embed.fields:
            match = re.search(r"ID de Sugerencia:\*\*\s*(\d+)", field.value or "")
            if match:
                return int(match.group(1))

        return None

    @discord.ui.button(
        label="✅",
        style=discord.ButtonStyle.success,
        custom_id="suggestion_vote_positive_btn",
        row=0
    )
    async def vote_positive(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, positive=True)

    @discord.ui.button(
        label="❌",
        style=discord.ButtonStyle.danger,
        custom_id="suggestion_vote_negative_btn",
        row=0
    )

    # Funciones encagadas del procesamiento de los votos
    async def vote_negative(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, positive=False)

    async def handle_vote(self, interaction: discord.Interaction, positive: bool):
        suggestion_id = self._extract_suggestion_id(interaction.message)
        if not suggestion_id:
            log.warning("No se pudo extraer el suggestion_id del mensaje.")
            return await safe_send(interaction, "❌ No se pudo identificar la sugerencia.")

        try:
            await interaction.response.defer(ephemeral=True)
        except (discord.errors.InteractionResponded, discord.errors.NotFound):
            return

        vote_type = "positive" if positive else "negative"
        user_id = str(interaction.user.id)

        try:
            texto_respuesta, nuevo_embed = await process_suggestion_vote(
                suggestion_id=suggestion_id,
                user_id=user_id,
                vote_type=vote_type
            )
            # Actualizar el embed con los nuevos votos y porcentajes en tiempo real
            await interaction.message.edit(embed=nuevo_embed, view=self)
            await interaction.followup.send(texto_respuesta, ephemeral=True)
            await self._ensure_thread_exists(interaction.message, suggestion_id)
            
        except ValueError as e:
            await interaction.followup.send(f"⚠️ {e}", ephemeral=True)
        except Exception as e:
            log.error(f"Error procesando voto en sugerencia #{suggestion_id}: {e}")
            await interaction.followup.send(
                "❌ Ocurrió un error al registrar tu voto en la base de datos.",
                ephemeral=True
            )

    # Funcion encargada de crear el hilo
    async def _ensure_thread_exists(self, message: discord.Message, suggestion_id: int | None = None) -> discord.Thread | None:
        """
        Verifica si el mensaje ya tiene un hilo adjunto. Si no lo tiene,
        crea uno automáticamente para la conversación de la sugerencia.
        """

        if message.thread is not None:
            return message.thread

        thread_name = f"💬 Discusión - Sugerencia #{suggestion_id}"

        try:
            thread = await message.create_thread(
                name = thread_name,
                reason = f"Discusión sobre la sugerencia #{suggestion_id}"
            )

            log.info(f"Hilo '{thread_name}' creado exitosamente para el mensaje {message.id}.")
            return thread

        except discord.Forbidden:
            log.warning(f"No se tienen permisos suficientes (Create Public Threads) para crear un hilo en {message.channel.id}.")
        except discord.HTTPException as e:
            log.error(f"Error HTTP al intentar crear un hilo en el mensaje {message.id}: {e}")
        except Exception as e:
            log.error(f"Error insospechado al crear el hilo: {e}")
