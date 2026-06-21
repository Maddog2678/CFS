import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

YOUR_CID = 1503970
YOUR_CALLSIGN = "RLTS3"
DISCORD_CHANNEL_ID = 1492743633982455874

last_online = False

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()

@tasks.loop(seconds=15)
async def check_vatsim():
    global last_online
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        current_online = False
        my_dep = "Unknown"

        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID and pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                current_online = True
                my_dep = pilot.get("flight_plan", {}).get("departure", "Unknown")
                break

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        if current_online and not last_online:
            embed = discord.Embed(
                title="🔵 RLTS Fleet Live Status",
                color=0x3498db,
                timestamp=discord.utils.utcnow()
            )
            embed.description = f"**RLTS3** is now connected to VATSIM!"
            embed.set_footer(text=f"Departing from: {my_dep}")
            await channel.send(embed=embed)

        last_online = current_online

    except Exception as e:
        print(f"Error: {e}")

@bot.command()
async def vatsim(ctx):
    """Manual RLTS check"""
    await check_vatsim()
    await ctx.send("✅ Checked VATSIM status!")

bot.run(os.getenv("TOKEN"))
