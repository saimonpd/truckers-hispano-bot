import discord

GAME_NAMES = {
    "ets2": "Euro Truck Simulator 2",
    "ats": "American Truck Simulator",
}

SERVER_NAMES = {
    "servpriv": "Servidor Privado",
    "TMP/SIM1": "TruckersMP | Simulador 1",
    "TMP/SIM2": "TruckersMP | Simulador 2",
    "TMP/ARC": "TruckersMP | Arcade",
    "PROMODS": "TruckersMP | Promods",
}

def build_route_embed(data: dict) -> discord.Embed:
    game = GAME_NAMES.get(data.get("game"))
    server = SERVER_NAMES.get(data.get("server"))
    dlc = data.get("required_dlc") or "No se requieren DLCs"
    date = data.get("discord_fecha")
    meeting = data.get("discord_reunion")
    departure = data.get("discord_salida")

    if data.get("game") == "ets2":
        title = f":flag_eu: Ruteo ETS2"
    else:
        title = f":flag_us: Ruteo ATS"

    embed = discord.Embed(title=title, color=discord.Color.green())

    if data.get("game") == "ets2":
        embed.add_field(
            name="📌 Información",
            value=(
                f"👤 Creador: <@{data.get('id_user') or data.get('author_id')}>\n"
                f":flag_eu: **Juego:** {game}\n"
                f"🖥️ **Servidor:** {server}\n"
            ),
            inline=False
        )
    else:
        embed.add_field(
            name="📌 Información",
            value=(
                f"👤 Creador: <@{data.get('id_user') or data.get('author_id')}>\n"
                f":flag_us: **Juego:** {game}\n"
                f"🖥️ **Servidor:** {server}\n"
            ),
            inline=False
        )

    embed.add_field(
        name="🗺️ Ruta",
        value=(
            f"🟢 **Salida:** Se decidirá en el momento"
        ),
        inline=False
    )

    embed.add_field(
        name="📦 DLCs",
        value=(
            f"{dlc}"
        ),
        inline=False
    )

    embed.add_field(
        name="🕐 Horario",
        value=(
            f"📅 **Fecha:** {date}\n"
            f"🟡 **Reunión:** {meeting}\n"
            f"🟢 **Salida:** {departure}\n"
        ),
        inline=False
    )

    participants = data.get("participants") or []
    participants_mentions = [f"<@{user_id}>" for user_id in participants]
    participants_text = "\n".join(participants_mentions) if participants_mentions else "Nadie se ha apuntado aún."
    embed.add_field(
        name=f"👥 Participantes ({len(participants)})",
        value=participants_text,
        inline=False
    )

    embed.set_footer(
        text="Truckers Hispano • Sistema de Ruteos"
    )

    return embed