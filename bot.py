import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# === YOUR DETAILS ===
YOUR_CID = 1503970
YOUR_CALLSIGN = "RLTS3"
DISCORD_CHANNEL_ID = 1492743633982455874   # General chat channel ID

last_seen = False

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    check_vatsim.start()

@tasks.loop(seconds=30)
async def check_vatsim():
    global last_seen
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        response.raise_for_status()
        data = response.json()
 
        online = False
        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID or pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                online = True
                break

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            if online and not last_seen:
                await channel.send(f"🚀 **{YOUR_CALLSIGN}** (CID {YOUR_CID}) has logged onto VATSIM! 🛫")
                last_seen = True
            elif not online and last_seen:
                last_seen = False

    except Exception as e:
        print(f"Error: {e}")

bot.run(os.getenv("TOKEN"))
