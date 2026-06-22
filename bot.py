import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Monitored callsigns (you can add more with !add)
monitored_callsigns = ["RLTS3", "RLTS", "RLTS2"]

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
        active = []

        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if any(cs.startswith(prefix) for prefix in [c.upper() for c in monitored_callsigns]):
                fp = pilot.get("flight_plan", {})
                dep = fp.get("departure", "?")
                arr = fp.get("arrival", "?")
                rlts_pilots.append(f"**{cs}** → {dep}→{arr}")

                if cs in [c.upper() for c in monitored_callsigns]:
                    active.append(cs)

        title = "🟢 RLTS Live Status" if active else "🔴 RLTS Live Status"
        color = 0x00ff00 if active else 0xff0000

        embed = discord.Embed(title=title, color=color, timestamp=discord.utils.utcnow())
        embed.description = "\n".join(rlts_pilots) if rlts_pilots else "No RLTS pilots online right now."

        if active:
            embed.set_footer(text=f"Active: {', '.join(active)}")
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
        print(f"Error: {e}")

@bot.command()
async def add(ctx, callsign: str):
    """Add a callsign to monitor. Example: !add RLTS4"""
    callsign = callsign.upper()
    if callsign not in monitored_callsigns:
        monitored_callsigns.append(callsign)
        await ctx.send(f"✅ Added **{callsign}** to monitoring list!")
    else:
        await ctx.send(f"**{callsign}** is already being monitored.")

@bot.command()
async def vatsim(ctx):
    """Refresh RLTS status"""
    await check_vatsim()
    await ctx.send("✅ Status refreshed!")

bot.run(os.getenv("TOKEN"))
