import discord
from database.models.suggestion import SuggestionStatus

def get_suggestion_color(status: str | None) -> discord.Color:
    """Retorna el color según el estado de la sugerencia."""
    status_obj = SuggestionStatus(status) if status else SuggestionStatus.PENDING
    return {
        SuggestionStatus.PENDING: discord.Color.light_grey(),
        SuggestionStatus.IN_REVISION: discord.Color.blue(),
        SuggestionStatus.APPROVED: discord.Color.green(),
        SuggestionStatus.DENIED: discord.Color.red(),
    }[status_obj]

def build_suggestion_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"💡 {data.get('title')}",
        description=data.get('description'),
        color=get_suggestion_color(data.get('status'))
    )

    embed.add_field(
        name="Información de la Sugerencia",
        value=(
            f"> 👤 **Autor:** <@{data.get('id_user')}>\n"
            f"> 🆔 **ID de Sugerencia:** {data.get('suggestion_id', data.get('id'))}\n"
            f"> 📊 **Estado:** {data.get('status')}\n"            
        ),
        inline=False
    )

    if data.get("moderator_answer"):
        embed.add_field(
            name=f"Respuesta de {data.get('moderator_name', 'Moderación')}",
            value=f"> {data.get('moderator_answer')}",
            inline=False
        )

    return embed