import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

print("TOKEN EXISTS:", "DISCORD_BOT_TOKEN" in os.environ)
print("TOKEN VALUE LENGTH:", len(os.environ.get("DISCORD_BOT_TOKEN", "")))
print("TOKEN PREVIEW:", repr(os.environ.get("DISCORD_BOT_TOKEN")))
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DATA_FILE = "countdown_months.json"

TARGET_YEAR = 2027
TARGET_MONTH = 2
TARGET_DAY = 13

TIMEZONE = ZoneInfo("Europe/Stockholm")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"sent_months": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def months_remaining(now: datetime) -> int:
    target = datetime(TARGET_YEAR, TARGET_MONTH, TARGET_DAY, tzinfo=TIMEZONE)

    # Om datumet redan passerat
    if now >= target:
        return 0

    months = (TARGET_YEAR - now.year) * 12 + (TARGET_MONTH - now.month)

    # Om vi ännu inte nått den 13:e denna månad så är det fortfarande ett helt extra månadsteg kvar
    if now.day < TARGET_DAY:
        return months
    elif now.day == TARGET_DAY:
        return months
    else:
        return months - 1


@bot.event
async def on_ready():
    print(f"Inloggad som {bot.user}")

    if not monthly_loop.is_running():
        monthly_loop.start()

    if not test_loop.is_running():
        test_loop.start()

@tasks.loop(minutes=10)
async def test_loop():
    now = datetime.now(TIMEZONE)
    target = datetime(TARGET_YEAR, TARGET_MONTH, TARGET_DAY, tzinfo=TIMEZONE)

    remaining = target - now

    if remaining.total_seconds() <= 0:
        return

    # månader kvar
    months = (TARGET_YEAR - now.year) * 12 + (TARGET_MONTH - now.month)
    if now.day > TARGET_DAY:
        months -= 1

    days = remaining.days

    CHANNEL_ID = 1496261996830523602   # <-- BYT
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except Exception as e:
            print("Kunde inte hitta kanal:", e)
            return

    await channel.send(
        f"@everyone {days} dagar på mr pontus straff",
        allowed_mentions=discord.AllowedMentions.none()
    )

    print(f"[TEST] {months} månader kvar")

@tasks.loop(minutes=30)
async def monthly_loop():
    now = datetime.now(TIMEZONE)
    target = datetime(TARGET_YEAR, TARGET_MONTH, TARGET_DAY, tzinfo=TIMEZONE)

    # Kör bara om måldatum inte passerat
    if now >= target:
        return

    # Vi vill bara skicka på den 13:e varje månad
    if now.day != TARGET_DAY:
        return

    months_left = months_remaining(now)

    # Vi vill bara skicka när det är minst 1 månad kvar
    if months_left <= 0:
        return

    data = load_data()
    sent_months = data.get("sent_months", [])

    # Använder t.ex. "10_months" som unik markering
    key = f"{months_left}_months"

    if key in sent_months:
        return

    # Hämta kanal genom ID
    CHANNEL_ID = 510858123968380929  
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except Exception as e:
            print(f"Kunde inte hitta kanal: {e}")
            return

    await channel.send(
        f"@everyone Pontus är nu frisläppt om {months_left} månader.",
        allowed_mentions=discord.AllowedMentions(everyone=True)
    )

    sent_months.append(key)
    data["sent_months"] = sent_months
    save_data(data)

    print(f"Skickade månadsmeddelande: {months_left} månader kvar")


@monthly_loop.before_loop
async def before_monthly_loop():
    await bot.wait_until_ready()

print("RUNNING FILE:", __file__)
bot.run(TOKEN)
