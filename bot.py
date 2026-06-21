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
        my_status = "Offline"
        my_remarks = ""

        for pilot in data.get("pilots", []):
            cs = pilot.get("callsign", "").upper()
            if cs.startswith("RLTS"):
                fp = pilot.get("flight_plan", {})
                dep = fp.get("departure", "?")
                arr = fp.get("arrival", "?")
                remarks = fp.get("remarks", "")

                line = f"**{cs}** → {dep}→{arr}"
                if "DISPLAY OPS" in remarks.upper() or "RTA" in remarks.upper():
                    line += f" | {remarks[:60]}"
                rlts_pilots.append(line)

                if pilot.get("cid") == YOUR_CID and cs == YOUR_CALLSIGN:
                    my_status = dep
                    my_remarks = remarks

        # Color logic
        color = 0x3498db if rlts_pilots else 0xe74c3c   # Blue if any RLTS, Red if none

        embed = discord.Embed(
            title="🟢 RLTS Fleet Live Status",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        embed.description = "\n".join(rlts_pilots) if rlts_pilots else "No RLTS pilots online right now."
        embed.set_footer(text=f"RLTS • RLTS3 departing: {my_status}")

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
    await ctx.send("✅ Status updated!")

bot.run(os.getenv("TOKEN"))
