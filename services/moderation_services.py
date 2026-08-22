import discord
import datetime
import logging

log = logging.getLogger("moderation")


async def kick(usuario: discord.Member, moderador: discord.Member, razon: str) -> bool:
    await usuario.kick(reason=f"{razon} | Por {moderador}")
    log.info(f"KICK ejecutado | {moderador} expulsó a {usuario} ({usuario.id}) | Razón: {razon}")
    return True


async def ban(usuario: discord.Member, moderador: discord.Member, razon: str) -> bool:
    await usuario.ban(reason=f"{razon} | Por {moderador}")
    log.info(f"BAN ejecutado | {moderador} baneó a {usuario} ({usuario.id}) | Razón: {razon}")
    return True


async def timeout(usuario: discord.Member, moderador: discord.Member, razon: str, minutos: int) -> bool:
    duracion = datetime.timedelta(minutes=minutos)
    await usuario.timeout(duracion, reason=f"{razon} | Por: {moderador}")
    log.info(f"TIMEOUT ejecutado | {moderador} aisló {minutos} min a {usuario} ({usuario.id}) | Razón: {razon}")
    return True


async def change_nickname(usuario: discord.Member, moderador: discord.Member, nuevo_nombre: str, razon: str) -> bool:
    nombre_anterior = usuario.display_name
    await usuario.edit(nick=nuevo_nombre, reason=f"{razon} | Por {moderador}")
    log.info(
        f"NICKNAME cambiado | {moderador} cambió el nick de {usuario} ({usuario.id}) "
        f"de '{nombre_anterior}' a '{nuevo_nombre}' | Razón: {razon}"
    )
    return True