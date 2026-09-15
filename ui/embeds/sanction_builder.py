import discord
from datetime import datetime

def sanction_confirmation_delete_embed(data: dict) -> discord.Embed:
    """
    data: {id, usuario_id, mod_id, razon, fecha}
    """
    embed = discord.Embed(
        title="⚠️ Confirmar eliminacion de sancion",
        description="¿Seguro que quieres eliminar esta sancion? Esta accion no se puede deshacer.",
        color=discord.Color.orange()
    )
    embed.add_field(name="ID", value=str(data.get("id")), inline=True)
    embed.add_field(name="Usuario", value=f"<@{data.get('usuario_id')}>", inline=True)
    embed.add_field(name="Moderador", value=f"<@{data.get('mod_id')}>", inline=True)
    embed.add_field(name="Razon", value=data.get("razon", "—"), inline=False)

    fecha = data.get("fecha")
    if fecha:
        embed.set_footer(text=f"Sancion creada el {fecha}")

    return embed


def sanction_list_embed(data: dict) -> discord.Embed:
    """
    data: {usuario_id, sanciones: [ {id, mod_id, razon, fecha}, ... ]}
    """
    usuario_id = data.get("usuario_id")
    sanciones = data.get("sanciones", [])

    embed = discord.Embed(
        title="📋 Sanciones del usuario",
        description=f"<@{usuario_id}> tiene **{len(sanciones)}** sancion(es) registrada(s)",
        color=discord.Color.red()
    )

    for sancion in sanciones[:25]:  # limite de 25 fields por embed
        fecha = sancion.get("fecha")
        fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if isinstance(fecha, datetime) else str(fecha)

        embed.add_field(
            name=f"ID {sancion.get('id')} — {fecha_str}",
            value=f"**Moderador:** <@{sancion.get('mod_id')}>\n**Razon:** {sancion.get('razon', '—')}",
            inline=False
        )

    return embed