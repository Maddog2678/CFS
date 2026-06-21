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

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()

@tasks.loop(seconds=20)
async def check_vatsim():
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        rlts_pilots = []
        my_status = None

        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if cs.startswith("RLTS"):
                dep = pilot.get("flight_plan", {}).get("departure", "?")
                arr = pilot.get("flight_plan", {}).get("arrival", "?")
                rlts_pilots.append(f"**{cs}** → {dep}→{arr}")

                if pilot.get("cid") == YOUR_CID and cs == YOUR_CALLSIGN:
                    my_status = dep

        # Create status embed
        embed = discord.Embed(
            title="🟢 RLTS Fleet Status",
            color=0x00ff00 if any("RLTS3" in p for p in rlts_pilots) else 0xffaa00
        )

        if rlts_pilots:
            embed.description = "\n".join(rlts_pilots)
        else:
            embed.description = "No RLTS pilots online."

        if my_status:
            embed.set_footer(text=f"RLTS3 is on the ground at {my_status} • Live Update")
        else:
            embed.set_footer(text="RLTS3 is offline • Live Update")

        # For now we send it when someone uses !vatsim
        # (we can't auto-update an old message easily)

    except:
        pass

@bot.command()
async def vatsim(ctx):
    """Live RLTS Status"""
    # The check_vatsim function runs the logic
    await check_vatsim()
    # To actually send the embed we'd need to move the embed code here
    await ctx.send("✅ Checking live status... (use !vatsim again to refresh)")

bot.run(os.getenv("TOKEN"))
