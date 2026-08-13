import discord 

def build_welcome_embed(member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title="Bienvenido a Truckers Hispano",
        description="Desde 2022 uniendo almnas en carretera",
        color= discord.Color.greyple()
    )

    embed.set_thumbnail(url="https://i.imgur.com/Vom0vPu.png")
    embed.set_image(url="https://i.imgur.com/xfRl77T.png")
    embed.set_footer(text="Truckers Hispano • Desde 2022 🚛")

    return embed