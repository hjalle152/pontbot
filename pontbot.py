import os
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks
from discord import app_commands

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DATA_FILE = "countdown_days.json"

TARGET_YEAR = 2027
TARGET_MONTH = 2
TARGET_DAY = 13

TIMEZONE = ZoneInfo("Europe/Stockholm")
CHANNEL_IDS = [
    1496261996830523602,
    1471654566582816769
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"last_sent_date": None}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def target_datetime():
    return datetime(TARGET_YEAR, TARGET_MONTH, TARGET_DAY, 0, 0, tzinfo=TIMEZONE)


def days_remaining(now: datetime) -> int:
    target = target_datetime()
    remaining = target - now
    return max(0, remaining.days)


# 🔥 FUN FACTS
PONTUS_FUN_FACTS = [
    "Pontus-fun fact: Pontus luktar bättre än Julis Qvarnström.",
    "Pontus-fun fact: Botten är gjord av Hjalmar, Hjalmar är bättre än Julius",
    "Pontus-fun fact: Pontus är född 1998 i Ingelstad.",
    "Pontus-fun fact: År 2021 uppmärksammades Rasmussons Youtube-kanal som en av de mest inflytelserika i Sverige och beskrevs som den femte mäktigaste i landet.",
    "Pontus-fun fact: Rasmussons kanaler stängdes ned av Youtube 2022 efter att Svenska Dagbladet publicerat en granskning av hans verksamhet.",
    "Pontus-fun fact: Som 15-åring släppte Pontus en egenproducerad EP på Spotify och började därefter publicera covers av poplåtar.",
    "Pontus-fun fact: I augusti 2021 publicerade Rasmusson en video på TikTok där han uppgav sig vara född 2004.",
    "Pontus-fun fact: Om jag tar din oskuld lämnar jag dig aldrig. Jag menar, varför skulle jag någonsin lämna en tjej som litade på mig med hennes kropp?",
    "Pontus-fun fact:I juli 2025 väckte Pontus Rasmusson ny debatt efter att ha startat ett konto på prenumerationsplattformen OnlyFans tillsammans med sin flickvän.",
    "Pontus-fun fact: År 2026 dömdes Pontus Rasmusson av Växjö tingsrätt till ett års fängelse och tre års näringsförbud för grovt bokföringsbrott. Han ålades även att betala en företagsbot om 50 000 kronor.",
    "Pontus-fun fact: Bajskorv hehe @rulltarat.",
]


@bot.event
async def on_ready():
    print(f"Inloggad som {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synkade {len(synced)} commands")
    except Exception as e:
        print(e)

    if not daily_loop.is_running():
        daily_loop.start()


# ✅ /tidkvar
@bot.tree.command(name="tidkvar", description="Visar hur många dagar som är kvar")
async def tidkvar(interaction: discord.Interaction):
    now = datetime.now(TIMEZONE)
    days_left = days_remaining(now)

    await interaction.response.send_message(
        f"Det är {days_left} dagar kvar av Pontus Rasmussons straff."
    )



@bot.tree.command(name="hjälp", description="Visar alla kommandon")
async def hjälp(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Kommandon:**\n"
        "/tidkvar - visar hur många dagar som är kvar\n"
        "/pontusfakta - slumpad fun fact\n"
        "/hjälp - visar denna lista"
    )



@bot.tree.command(name="pontusfakta", description="Slumpad fun fact")
async def pontusfakta(interaction: discord.Interaction):
    fact = random.choice(PONTUS_FUN_FACTS)
    await interaction.response.send_message(fact)



@tasks.loop(minutes=1)
async def daily_loop():
    now = datetime.now(TIMEZONE)
    target = target_datetime()

    if now >= target:
        return

    if not (now.hour == 12 and now.minute == 0):
        return

    data = load_data()
    today_key = now.strftime("%Y-%m-%d")

    if data.get("last_sent_date") == today_key:
        return

    days_left = days_remaining(now)

    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)

        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                print(f"Kunde inte hitta kanal {channel_id}: {e}")
                continue

        await channel.send(
            f"@everyone nu är det {days_left} dagar kvar av Pontus Rasmussons straff.",
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )

    data["last_sent_date"] = today_key
    save_data(data)

    print(f"Skickade dagsmeddelande: {days_left} dagar kvar")


@daily_loop.before_loop
async def before_daily_loop():
    await bot.wait_until_ready()


bot.run(TOKEN)
