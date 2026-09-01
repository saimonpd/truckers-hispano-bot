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
        title=f"📩 NUEVA SUGERENCIA RECIBIDA | {data.get('user_name')}",
        description=data.get('description'),
        color=get_suggestion_color(data.get('status'))
    )

    # Obtener votos
    pos_votes = int(data.get("positive_votes") or 0)
    neg_votes = int(data.get("negative_votes") or 0)
    total_votes = pos_votes + neg_votes

    # Calcular porcentajes de votos
    if total_votes > 0:
        pos_percent = round((pos_votes / total_votes) * 100, 1)
        neg_percent = round((neg_votes / total_votes) * 100, 1)
    else:
        pos_percent = 0.0
        neg_percent = 0.0

    embed.add_field(
        name="\n📊 Votación de la Comunidad",
        value=(
            f"✅ **A favor:** `{pos_votes} ({pos_percent}%)`     ❌ **En contra:** `{neg_votes} ({neg_percent}%)`\n"
            f"👥 **Total de votos:** `{total_votes}`"
        ),
        inline=False
    )

    # Campo de respuesta del moderador (si existe)
    if data.get("moderator_answer"):
        embed.add_field(
            name=f"\n👮 Respuesta de {data.get('moderator_name', 'Moderación')}",
            value=f"> {data.get('moderator_answer')}",
            inline=False
        )

    # Footer con ID de sugerencia
    suggestion_id = data.get("suggestion_id") or data.get("id") or "N/A"
    embed.set_footer(
        text=f"ID: {suggestion_id} • Usa '/crear_sugerencia' para enviar una sugerencia"
    )

    return embed