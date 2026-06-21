import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True  # Needed for commands
bot = commands.Bot(command_prefix='!', intents=intents)

# === YOUR DETAILS ===
YOUR_CID = 1503970
YOUR_CALLSIGN = "RLTS3"
DISCORD_CHANNEL_ID = 1492743633982455874

last_online = False

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    check_vatsim.start()

@tasks.loop(seconds=30)
async def check_vatsim():
    global last_online
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        response.raise_for_status()
        data = response.json()

        current_online = False
        pilot_data = None

        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID or pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                current_online = True
                pilot_data = pilot
                break

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        if current_online and not last_online:
            callsign = pilot_data.get("callsign", YOUR_CALLSIGN)
            fp = pilot_data.get("flight_plan", {})
            dep = fp.get("departure", "Unknown")
            arr = fp.get("arrival", "Unknown")
            ac = fp.get("aircraft_short", "Unknown")
            alt = pilot_data.get("altitude", 0)

            if dep != "Unknown" and arr != "Unknown":
                msg = f"🚀 **{callsign}** is online!\n**Route:** {dep} → {arr}\n**Aircraft:** {ac} | **Alt:** {alt:,} ft"
            else:
                msg = f"🚀 **{callsign}** has logged onto VATSIM!"

            await channel.send(msg)

        last_online = current_online

    except Exception as e:
        print(f"Error: {e}")

@bot.command()
async def vatsim(ctx):
    """Manual VATSIM status check"""
    await check_vatsim()
    await ctx.send("✅ Checked VATSIM status!")

bot.run(os.getenv("TOKEN"))
