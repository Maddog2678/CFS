import discord
from discord.ext import tasks, commands
import requests
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Your details - CHANGE THESE
YOUR_CID = 1503970         # Your VATSIM CID (number)
YOUR_CALLSIGN = "RLTS3"  # e.g. "ABC123"
DISCORD_CHANNEL_ID = 1492743633982455874 # Right-click channel → Copy ID (Developer Mode on)

last_seen = False  # Track state to avoid repeated pings

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()  # Start the background task

@tasks.loop(seconds=30)  # Check every 30 seconds (respect rate limits)
async def check_vatsim():
    global last_seen
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        response.raise_for_status()
        data = response.json()

        # Look for your CID or callsign in pilots
        online = False
        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID or pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                online = True
                break

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("Channel not found!")
            return

        if online and not last_seen:
            # Just logged on
            await channel.send(f"🚀 **{YOUR_CALLSIGN}** (CID {YOUR_CID}) has logged onto VATSIM! 🛫")
            last_seen = True
        elif not online and last_seen:
            # Logged off (optional notification)
            # await channel.send(f"👋 {YOUR_CALLSIGN} has left VATSIM.")
            last_seen = False

    except Exception as e:
        print(f"Error checking VATSIM: {e}")

# Optional: Manual check command
@bot.command()
async def vatsim(ctx):
    """Manual check if you're online."""
    await check_vatsim()
    await ctx.send("Checked VATSIM status.")

import os
bot.run(os.getenv("MTUxODIyNDk5OTMxNDM2MjQ1OA.G5tsY4.5oemBtvucyG_BT_BNY3J0lmmw1cl5UwZcex7Ng"))