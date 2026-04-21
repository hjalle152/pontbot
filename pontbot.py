import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DATA_FILE = "countdown_days.json"

TARGET_YEAR = 2027
TARGET_MONTH = 2
TARGET_DAY = 13

TIMEZONE = ZoneInfo("Europe/Stockholm")
CHANNEL_ID = 1496261996830523602

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
    return remaining.days


@bot.event
async def on_ready():
    print(f"Inloggad som {bot.user}")
    if not daily_loop.is_running():
        daily_loop.start()


@tasks.loop(minutes=1)
async def daily_loop():
    now = datetime.now(TIMEZONE)
    target = target_datetime()

    if now >= target:
        return

    # Endast kl 12:00
    if not (now.hour == 12 and now.minute == 0):
        return

    data = load_data()
    today_key = now.strftime("%Y-%m-%d")

    # Undvik att skicka flera gånger samma dag
    if data.get("last_sent_date") == today_key:
        return

    days_left = days_remaining(now)

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except Exception as e:
            print(f"Kunde inte hitta kanal: {e}")
            return

    await channel.send(
        f"@everyone nu är det {days_left} dagar kvar av Pontus Rasmussons straff.",
        allowed_mentions=discord.AllowedMentions(everyone=True)
    )

    data["last_sent_date"] = today_key
    save_data(data)

    print(f"Skickade dagsmeddelande: {days_left} dagar kvar")

    await channel.send(
        f"@everyone nu är det {days_left} dagar kvar av Pontus Rasmussons straff.",
        allowed_mentions=discord.AllowedMentions(everyone=True)
    )

    data["sent_times"].append(current_key)

    # håll listan liten
    if len(data["sent_times"]) > 50:
        data["sent_times"] = data["sent_times"][-50:]

    save_data(data)

    print(f"Skickade dagsmeddelande: {current_key} - {days_left} dagar kvar")


@daily_loop.before_loop
async def before_daily_loop():
    await bot.wait_until_ready()


bot.run(TOKEN)
