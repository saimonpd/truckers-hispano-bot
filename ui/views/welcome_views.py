import discord

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
        self.add_item(discord.ui.Button(
            label="🌐 Web",
            style=discord.ButtonStyle.link,
            url="https://sites.google.com/view/truckershispano?usp=sharing",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="📸 Instagram",
            style=discord.ButtonStyle.link,
            url="https://www.instagram.com/truckershispano/",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="▶️ Youtube",
            style=discord.ButtonStyle.link,
            url="https://www.youtube.com/@TruckersHispano",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="🐦 Twitter",
            style=discord.ButtonStyle.link,
            url="https://x.com/TruckersHispano",
            row=1
        ))
        self.add_item(discord.ui.Button(
            label="🎵 TikTok",
            style=discord.ButtonStyle.link,
            url="https://www.tiktok.com/@truckers.hispano",
            row=1
        ))