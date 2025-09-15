# modules/greetings.py

import json
import random
from pathlib import Path
from discord.ext import commands
import discord
import config

# Pfad zum datenbank-Ordner, in dem die JSON-Dateien liegen
BASE = Path(__file__).parent.parent / "datenbank"

def load_json(file_name: str):
    path = BASE / file_name
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def setup(bot: commands.Bot):
    # Lade Begrüßungs- und Abschiedsnachrichten
    welcome_texts = load_json("Willkommen.json")
    goodbye_texts = load_json("Wiedersehen.json")

    @bot.event
    async def on_member_join(member: discord.Member):
        channel = bot.get_channel(config.WELCOME_CHANNEL_ID)
        if channel and welcome_texts:
            # Wähle zufälligen Eintrag und ersetze Platzhalter
            text = random.choice(list(welcome_texts.values()))
            await channel.send(text.replace("member", member.mention))

    @bot.event
    async def on_member_remove(member: discord.Member):
        channel = bot.get_channel(config.GOODBYE_CHANNEL_ID)
        if channel and goodbye_texts:
            text = random.choice(list(goodbye_texts.values()))
            await channel.send(text.replace("member", member.name))
