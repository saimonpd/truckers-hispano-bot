# bot-truckers-hispano
A Discord bot designed to automate repetitive tasks and community management, making moderators work easier while improving the overall user experience.

## Features
* Welcome System
When a new member joins the server, the bot automatically:
- Assigns a default role
- Sends a welcome message 
- Displays a persistent set of link buttons

## Architecture
The project follows a layered structure to keep Discord separate from business logic:

cogs/           -> Listens to Discord events, delegates to services
services/       -> Business logic
ui/
    embeds/     -> Embed builders (presentation logic messages) 
    views/      -> Discord UI components
config/         -> Centralized configuration

Why this architecture?
- Cogs only job is to listen for a Dsicord event and hanfd off to a service
- Services contain the actual logic business

Cogs are auto-loaded on main by recursively scanning the cogs/ directory and persistent vies are registered in setup_hook to avoid interaction failures after restarts.

## Tech Stack
- Python 3.14
- discord.py
- logging
- python-dotenv

## Setup and Installation
Prerequisites:
- Python 3.14
- A discord bot application with de Server Members Intent enabled in the Discord Developar Portal

Installation:
git clone https://github.com/<your-username>/Discord-bot-Truckers-Hispano.git
cd Discord-bot-Truckers-Hispano
pip install -r requirements.txt

Configuration:
Create your configuration values using the .env.example

Update config/channels.py and config/roles.py with the correct IDs for your server

Running the bot:
python main.py

On startup, the bot will:
1. Load all cogs found under cogs/
2. Register persistent views
3. Sync slash commands with Discord
4. Connect and log Bot connected: <bot_name>

