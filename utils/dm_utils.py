import discord

async def send_dm(user: discord.Member, title: str, description: str):
    try:
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red()
        )
        await user.send(embed=embed)
        return True
    except Exception:
        return False