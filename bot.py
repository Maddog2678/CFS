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
            # Just logged on
            callsign = pilot_data.get("callsign", YOUR_CALLSIGN)
            fp = pilot_data.get("flight_plan", {})
            departure = fp.get("departure", "Unknown")
            arrival = fp.get("arrival", "Unknown")
            aircraft = fp.get("aircraft_short", "Unknown")
            altitude = pilot_data.get("altitude", 0)

            if departure != "Unknown" and arrival != "Unknown":
                msg = f"🚀 **{callsign}** has logged onto VATSIM!\n" \
                      f"**Flight:** {departure} → {arrival}\n" \
                      f"**Aircraft:** {aircraft} | **Altitude:** {altitude:,} ft"
            else:
                msg = f"🚀 **{callsign}** has logged onto VATSIM!"

            await channel.send(msg)

        last_online = current_online

    except Exception as e:
        print(f"Error: {e}")

bot.run(os.getenv("TOKEN"))
