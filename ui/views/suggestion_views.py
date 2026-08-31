import re
import logging
import discord
from database.repositories.suggestion_repository import update_vote
from utils.safe_send import safe_send

log = logging.getLogger("suggestions")

class SuggestionView(discord.ui.View):
    def __init__(self, suggestion_id: int | None = None):
        super().__init__(timeout=None)
        self.suggestion_id = suggestion_id

    # Funcion encargada de identificar el ID de la sugerencia para asignarle el voto
    def _extract_suggestion_id(self, message: discord.Message | None) -> int | None:
        if self.suggestion_id is not None:
            return self.suggestion_id

        if not message or not message.embeds:
            return None

        embed = message.embeds[0]
        for field in embed.fields:
            match = re.search(r"ID de Sugerencia:\*\*\s*(\d+)", field.value or "")
            if match:
                return int(match.group(1))

        if embed.footer and embed.footer.text:
            match = re.search(r"(\d+)", embed.footer.text)
            if match:
                return int(match.group(1))

        return None

    @discord.ui.button(
        label="👍",
        style=discord.ButtonStyle.success,
        custom_id="suggestion_vote_positive_btn",
        row=0
    )
    async def vote_positive(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, positive=True)

    @discord.ui.button(
        label="👎",
        style=discord.ButtonStyle.danger,
        custom_id="suggestion_vote_negative_btn",
        row=0
    )
    async def vote_negative(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, positive=False)


    async def handle_vote(self, interaction: discord.Interaction, positive: bool):
        suggestion_id = self._extract_suggestion_id(interaction.message)
        if not suggestion_id:
            log.warning("No se pudo extraer el suggestion_id del mensaje.")
            return await safe_send(interaction, "❌ No se pudo identificar la sugerencia.")

        vote_type = "positive" if positive else "negative"
        user_id = str(interaction.user.id)

        exito = update_vote(suggestion_id=suggestion_id, user_id=user_id, vote_type=vote_type)

        if exito:
            tipo_txt = "positivo" if positive else "negativo"
            await safe_send(interaction, f"✅ Has votado **{tipo_txt}** en la sugerencia.")
        else:
            await safe_send(interaction, "❌ Ocurrió un error al registrar tu voto en la base de datos.")