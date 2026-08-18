import discord
import datetime

async def kick (usuario: discord.Member, moderador: discord.Member, razon: str) -> bool:
    await usuario.kick(reason=f"{razon} | Por {moderador}")


async def ban (usuario: discord.Member, moderador: discord.Member, razon: str) -> bool:
    await usuario.ban(reason=f"{razon} | Por {moderador}")

async def timeout(usuario: discord.Member, moderador: discord.Member, razon: str, minutos: int) -> bool:
    duracion = datetime.timedelta(minutes=minutos)
    await usuario.timeout(duracion, reason=f"{razon} | Por: {moderador}")

async def change_nickname(usuario: discord.Member, moderador: discord.Member, nuevo_nombre: str, razon: str) -> bool:
    await usuario.edit(nick=nuevo_nombre, reason=f"{razon} | Por {moderador}")