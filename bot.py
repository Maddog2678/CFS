import discord
from discord.ext import tasks, commands
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# === MONITORED PILOTS ===
PILOTS = [
    {"cid": 1490415, "callsign": "RLTS", "name": "RLTS"},
    {"cid": 1919216, "callsign": "RLTS2", "name": "RLTS2"},
    {"cid": 1503970, "callsign": "RLTS3", "name": "RLTS3"}
]

DISCORD_CHANNEL_ID = 1492743633982455874

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    check_vatsim.start()

@tasks.loop(seconds=15)
async def check_vatsim():
    try:
        response = requests.get("https://data.vatsim.net/v3/vatsim-data.json", timeout=10)
        data = response.json()

        rlts_pilots = []

        for pilot_info in PILOTS:
            cid = pilot_info["cid"]
            callsign = pilot_info["callsign"]
            name = pilot_info["name"]

            for pilot in data.get("pilots", []):
                if pilot.get("cid") == cid and pilot.get("callsign", "").upper() == callsign.upper():
                    fp = pilot.get("flight_plan", {})
                    dep = fp.get("departure", "?")
                    arr = fp.get("arrival", "?")
                    rlts_pilots.append(f"**{name}** → {dep}→{arr}")
                    break

        # Dynamic title and color
        if rlts_pilots:
            title = "🟢 RLTS Live Status"
            color = 0x00ff00
        else:
            title = "🔴 RLTS Live Status"
            color = 0xff0000

        embed = discord.Embed(title=title, color=color, timestamp=discord.utils.utcnow())
        embed.description = "\n".join(rlts_pilots) if rlts_pilots else "No RLTS pilots online right now."
        embed.set_footer(text="Live Update • Every 15 seconds")

        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            return

        # Delete old messages first
        async for message in channel.history(limit=10):
            if message.author == bot.user and message.embeds:
                if "RLTS Live Status" in message.embeds[0].title:
                    await message.delete()

        # Send new one
        await channel.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")

@bot.command()
async def vatsim(ctx):
    await check_vatsim()
    await ctx.send("✅ Status refreshed!")

bot.run(os.getenv("TOKEN"))
