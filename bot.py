import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# === YOUR DETAILS ===
YOUR_CID = 1503970
YOUR_CALLSIGN = "RLTS3"
DISCORD_CHANNEL_ID = 1492743633982455874

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

        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID or pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                callsign = pilot.get("callsign", YOUR_CALLSIGN)
                aircraft = pilot.get("flight_plan", {}).get("aircraft_short", "Unknown")
                departure = pilot.get("flight_plan", {}).get("departure", "Unknown")
                arrival = pilot.get("flight_plan", {}).get("arrival", "Unknown")
                altitude = pilot.get("altitude", 0)

                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                if channel and not last_seen:
                    if departure != "Unknown" and arrival != "Unknown":
                        msg = f"🚀 **{callsign}** is now online!\n" \
                              f"**Route:** {departure} → {arrival}\n" \
                              f"**Aircraft:** {aircraft}\n" \
                              f"**Altitude:** {altitude:,} ft"
                    else:
                        msg = f"🚀 **{callsign}** has logged onto VATSIM!"

                    await channel.send(msg)
                    last_seen = True
                return  # Found the user

        # Not online
        if last_seen:
            last_seen = False

    except Exception as e:
        print(f"Error: {e}")

bot.run(os.getenv("TOKEN"))
