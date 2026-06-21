import discord
from discord.ext import tasks, commands
import requests
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

YOUR_CID = 1503970
YOUR_CALLSIGN = "RLTS3"
DISCORD_CHANNEL_ID = 1492743633982455874

status_message = None

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()
    # Send initial status message
    await asyncio.sleep(5)
    await send_or_update_status()

@tasks.loop(seconds=15)
async def check_vatsim():
    await send_or_update_status()

async def send_or_update_status():
    global status_message
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        rlts_pilots = []
        my_dep = "Offline"

        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if cs.startswith("RLTS"):
                dep = pilot.get("flight_plan", {}).get("departure", "?")
                arr = pilot.get("flight_plan", {}).get("arrival", "?")
                rlts_pilots.append(f"**{cs}** → {dep}→{arr}")

                if pilot.get("cid") == YOUR_CID and cs == YOUR_CALLSIGN:
                    my_dep = dep

        embed = discord.Embed(
            title="🟢 RLTS Fleet Live Status",
            color=0x00ff00 if my_dep != "Offline" else 0xffaa00,
            timestamp=discord.utils.utcnow()
        )

        embed.description = "\n".join(rlts_pilots) if rlts_pilots else "No RLTS pilots online."
        embed.set_footer(text=f"RLTS3 departing: {my_dep} | Updates every 15s")

        channel = bot.get_channel(DISCORD_CHANNEL_ID)

        if status_message:
            try:
                await status_message.edit(embed=embed)
            except:
                status_message = await channel.send(embed=embed)
        else:
            status_message = await channel.send(embed=embed)

    except Exception as e:
        print(f"Status update error: {e}")

@bot.command()
async def vatsim(ctx):
    await send_or_update_status()
    await ctx.send("✅ Live status updated!")

bot.run(os.getenv("TOKEN"))
