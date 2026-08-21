import discord

DIVIDER = "➖" * 15

def build_event_embed(data: dict) -> discord.Embed:
    """
    Construye un Embed limpio y profesional para eventos/convoys.
    Recibe el diccionario `data` unificado.
    """
    embed = discord.Embed(
        title=f"📢 {data.get('titulo', 'Evento VTC')}",
        description=data.get('descripcion', ''),
        color=discord.Color.blue()
    )

    # 1. Información General
    embed.add_field(
        name="🎮 Información General",
        value=(
            f"🎮 **Juego:** {data.get('juego_name', data.get('juego', 'N/A'))}\n"
            f"🤝 **Tipo:** {data.get('tipo_evento', 'Convoy')}\n"
            f"🏢 **Organiza:** {data.get('organizador', 'Staff')}\n"
            f"🌍 **Servidor:** {data.get('servidor_name', data.get('servidor', 'N/A'))}\n"
            f"{DIVIDER}"
        ),
        inline=False
    )

    # 2. Fecha y Horarios (soporta Timestamps de Discord si existen)
    reunion_str = data.get('discord_reunion', f"{data.get('hora_reunion')} 🇪🇸")
    salida_str = data.get('discord_salida', f"{data.get('hora_salida')} 🇪🇸")

    embed.add_field(
        name="📅 Fecha y Horarios",
        value=(
            f"🗓️ **Fecha:** {data.get('fecha')}\n"
            f"🧍 **Reunión:** {reunion_str}\n"
            f"🚦 **Salida:** {salida_str}\n"
            f"{DIVIDER}"
        ),
        inline=False
    )

    # 3. Ruta y Requisitos
    embed.add_field(
        name="📍 Ruta y Logística",
        value=(
            f"🟢 **Origen:** {data.get('ruta_origen', data.get('salida', 'N/A'))}\n"
            f"🔴 **Destino:** {data.get('ruta_destino', data.get('destino', 'N/A'))}\n"
            f"⛔ **Parada Intermedia:** {data.get('parada_intermedio', 'Ninguna')}\n"
            f"📜 **DLCs:** {data.get('dlcs_requeridos', 'No requeridos')}\n"
            f"{DIVIDER}"
        ),
        inline=False
    )

    # 4. Detalle de Carga
    embed.add_field(
        name="📦 Carga y Remolque",
        value=(
            f"📦 **Carga:** {data.get('carga', 'Libre')}\n"
            f"🛻 **Remolque:** {data.get('trailer', 'Libre')}\n"
            f"{DIVIDER}"
        ),
        inline=False
    )

    # 5. Normativa y Consejos
    embed.add_field(
        name="🚦 Normativa",
        value=(
            f"🚦 **Velocidad Máx:** 90 km/h\n"
            f"📏 **Distancia:** Mantener margen de seguridad\n"
            f"📌 Respetar las normas de TruckersMP y las indicaciones del Staff.\n"
            f"{DIVIDER}"
        ),
        inline=False
    )

    # 6. Lista de Participantes
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

    # Imagen y Miniatura opcionales
    if data.get("ruta_imagen"):
        embed.set_image(url=data["ruta_imagen"])

    embed.set_thumbnail(url="https://i.imgur.com/K3P7T3D.png")
    embed.set_footer(text="Truckers Hispano • Sistema de Eventos")

    return embed