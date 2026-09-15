import discord
import logging

log = logging.getLogger("sanctions")


class SanctionConfirmationDeleteView(discord.ui.View):
    def __init__(self, id_sancion: int, mod_id: int, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.id_sancion = id_sancion
        self.mod_id = mod_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Solo el moderador que pidio el borrado puede confirmar/cancelar
        if interaction.user.id != self.mod_id:
            await interaction.response.send_message(
                "No puedes interactuar con esta confirmacion", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Import diferido para evitar dependencia circular con el service
        from services.sanction_services import sanction_delete_confirm

        await interaction.response.defer()

        resultado = await sanction_delete_confirm(self.id_sancion)

        for item in self.children:
            item.disabled = True

        await interaction.edit_original_response(content=resultado, embed=None, view=self)
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(content="Eliminacion cancelada", embed=None, view=self)
        self.stop()


def sanction_confirmation_delete_view(data: dict) -> SanctionConfirmationDeleteView:
    return SanctionConfirmationDeleteView(
        id_sancion=data.get("id_sancion"),
        mod_id=data.get("mod")
    )