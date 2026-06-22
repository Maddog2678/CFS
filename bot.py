import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# === MONITORED PILOTS (in order) ===
PILOTS = [
    {"cid": 1490415, "callsign": "RLTS", "name": "RLTS"},
    {"cid": 1919216, "callsign": "RLTS2", "name": "RLTS2"},
    {"cid": 1503970, "callsign": "RLTS3", "name": "RLTS3"}
]

DISCORD_CHANNEL_ID = 1492743633982455874

last_online = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    for p in PILOTS:
        last_online[p["cid"]] = False
    check_vatsim.start()

@tasks.loop(seconds=15)
async def check_vatsim():
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        for pilot_info in PILOTS:
            cid = pilot_info["cid"]
            callsign = pilot_info["callsign"]
            name = pilot_info["name"]

            current_online = False
            my_dep = "Unknown"

            for pilot in data.get("pilots", []):
                if pilot.get("cid") == cid and pilot.get("callsign", "").upper() == callsign.upper():
                    current_online = True
                    my_dep = pilot.get("flight_plan", {}).get("departure", "Unknown")
                    break

            if current_online and not last_online.get(cid, False):
                embed = discord.Embed(
                    title="🟢 RLTS Live Status",
                    color=0x00ff00,
                    timestamp=discord.utils.utcnow()
                )
                embed.description = f"**{name}** is now connected to VATSIM!"
                embed.set_footer(text=f"Departing from: {my_dep}")
                await channel.send(embed=embed)

            last_online[cid] = current_online

    except Exception as e:
        print(f"Error: {e}")

@bot.command()
async def vatsim(ctx):
    """Show all RLTS pilots"""
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        rlts_list = []
        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if cs.startswith("RLTS"):
                fp = pilot.get("flight_plan", {})
                dep = fp.get("departure", "?")
                arr = fp.get("arrival", "?")
                rlts_list.append(f"**{cs}** → {dep}→{arr}")

        embed = discord.Embed(
            title="🟢 RLTS Pilots Online",
            color=0x00ff00
        )
        embed.description = "\n".join(rlts_list) if rlts_list else "No RLTS pilots online."
        await ctx.send(embed=embed)

    except:
        await ctx.send("❌ Could not reach VATSIM.")

bot.run(os.getenv("TOKEN"))
