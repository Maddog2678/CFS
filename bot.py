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

status_message = None

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()

@tasks.loop(seconds=15)
async def check_vatsim():
    global status_message
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        rlts_pilots = []
        my_dep = None
        any_rlts_online = False

        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if cs.startswith("RLTS"):
                any_rlts_online = True
                fp = pilot.get("flight_plan", {})
                dep = fp.get("departure", "?")
                arr = fp.get("arrival", "?")
                rlts_pilots.append(f"**{cs}** → {dep}→{arr}")

                if pilot.get("cid") == YOUR_CID and cs == YOUR_CALLSIGN:
                    my_dep = dep

        # Title with dynamic dot
        if any_rlts_online:
            title = "🟢 RLTS Live Status"
        else:
            title = "🔴 RLTS Live Status"

        embed = discord.Embed(
            title=title,
            color=0x00ff00 if any_rlts_online else 0xff0000,   # Green or Red
            timestamp=discord.utils.utcnow()
        )

        embed.description = "\n".join(rlts_pilots) if rlts_pilots else "No RLTS pilots online right now."

        if my_dep:
            embed.set_footer(text=f"RLTS Departing: {my_dep}")
        else:
            embed.set_footer(text="RLTS • No activity")

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if status_message:
            try:
                await status_message.edit(embed=embed)
            except:
                status_message = await channel.send(embed=embed)
        else:
            status_message = await channel.send(embed=embed)

    except Exception as e:
        print(f"Update error: {e}")

@bot.command()
async def vatsim(ctx):
    """Refresh RLTS status"""
    await check_vatsim()
    await ctx.send("✅ Status refreshed!")

bot.run(os.getenv("TOKEN"))
