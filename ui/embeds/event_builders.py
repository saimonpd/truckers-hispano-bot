import discord

def build_event_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(
        description=data.get('descripcion'),
        color=discord.Color.greyple()
    )

    embed.add_field(
        name="Información",
        value=(
            f"> 🎮 **Juego:** {data.get('juego_name', data.get('juego'))}\n"
            f"> 🏢 **Organiza:** {data.get('organizador')}\n"
            f"> 🌍 **Servidor:** {data.get('servidor_name', data.get('servidor'))}\n"
        ),
        inline=False
    )

    # Timestamps discord
    reunion_str = data.get('discord_reunion', f"{data.get('hora_reunion')} 🇪🇸")
    salida_str = data.get('discord_salida', f"{data.get('hora_salida')} 🇪🇸")

    embed.add_field(
        name="Fecha y Horarios",
        value=(
            f"> 🗓️ {data.get('fecha')}\n"
            f"> 🧍 **Reunión:** {reunion_str}\n"
            f"> 🚦 **Salida:** {salida_str}\n"
            "> Horario adaptado a tu zona horaria."
        ),
        inline=False
    )

    embed.add_field(
        name="Ruta",
        value=(
            f"> 🟢 **Origen:** {data.get('ruta_origen', data.get('salida'))}\n"
            f"> 🔴 **Destino:** {data.get('ruta_destino', data.get('destino'))}\n"
            f"> ⛔ **Parada Intermedia:** {data.get('parada_intermedio')}\n"
            f"> 📜 **DLCs:** {data.get('dlcs_requeridos')}\n"
        ),
        inline=False
    )

    embed.add_field(
        name="Carga y Remolque",
        value=(
            f"> 📦 **Carga:** {data.get('carga')}\n"
            f"> 🛻 **Remolque:** {data.get('trailer')}\n"
        ),
        inline=False
    )

    embed.add_field(
        name="",
        value=(
            f":vertical_traffic_light: **Velocidad máxima:** 90 km/h\n"
            f":straight_ruler: **Norma obligatoria:** Mantener distancia de seguridad\n"
            f":heavy_minus_sign: :heavy_minus_sign: :heavy_minus_sign: :heavy_minus_sign: :heavy_minus_sign: "
        ),
        inline=False
    )

    participantes = data.get("participantes", [])
    if participantes:
        # Muestra menciones separadas por espacio o salto de línea
        lista_users = "\n".join([f"• <@{uid}>" for uid in participantes])
    else:
        lista_users = "*Aún no hay inscritos. ¡Sé el primero!*"

    embed.add_field(
        name=f"👥 Confirmados ({len(participantes)})",
        value=lista_users,
        inline=False
    )

    if data.get("ruta_imagen"):
        embed.set_image(url=data["ruta_imagen"])

    embed.set_thumbnail(url="https://i.imgur.com/K3P7T3D.png")
    embed.set_footer(text="Truckers Hispano • Sistema de Eventos")

    return embed