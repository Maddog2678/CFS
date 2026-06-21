import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
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

@tasks.loop(seconds=15)   # Fastest safe speed
async def check_vatsim():
    global last_online
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=8)
        response.raise_for_status()
        data = response.json()

        current_online = False
        pilot_data = None

        for pilot in data.get("pilots", []):
            if pilot.get("cid") == YOUR_CID and pilot.get("callsign", "").upper() == YOUR_CALLSIGN.upper():
                current_online = True
                pilot_data = pilot
                break

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        if current_online and not last_online:
            fp = pilot_data.get("flight_plan", {})
            dep = fp.get("departure", "Unknown")
            arr = fp.get("arrival", "Unknown")

            if dep != "Unknown" and arr != "Unknown":
                msg = f"✈️ **{YOUR_CALLSIGN}** On the ground at **{dep}** → **{arr}**"
            else:
                msg = f"✈️ **{YOUR_CALLSIGN}** is now connected to VATSIM!"

            await channel.send(msg)

        last_online = current_online

    except Exception as e:
        print(f"Error: {e}")

@bot.command()
async def vatsim(ctx):
    """Show all RLTS callsigns currently online"""
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        rlts_pilots = []
        for pilot in data.get("pilots", []):
            callsign = pilot.get("callsign", "").upper()
            if callsign.startswith("RLTS"):
                fp = pilot.get("flight_plan", {})
                route = f"{fp.get('departure','?')}→{fp.get('arrival','?')}" if fp.get('departure') else "No flight plan"
                rlts_pilots.append(f"**{callsign}** → {route}")

        if rlts_pilots:
            embed = discord.Embed(title="🟢 RLTS Pilots Online", color=0x00ff00)
            embed.description = "\n".join(rlts_pilots)
            embed.set_footer(text=f"Total online: {len(rlts_pilots)}")
        else:
            embed = discord.Embed(title="🟡 No RLTS Online", description="No RLTS callsigns are currently flying.", color=0xffaa00)

        await ctx.send(embed=embed)

    except:
        await ctx.send("❌ Could not reach VATSIM right now.")

bot.run(os.getenv("TOKEN"))
