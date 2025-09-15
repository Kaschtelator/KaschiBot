# modules/moderation.py

import re
from pathlib import Path
from discord.ext import commands

# Basis-Verzeichnis für Wortlisten: ../datenbank relative zu modules/
BASE = Path(__file__).parent.parent / "datenbank"

def load_list(file_name: str):
    path = BASE / file_name
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

def setup(bot: commands.Bot):
    # toxische Wörter und Drohungsmuster laden
    TOXIC_WORDS = set(load_list("bad_words.txt"))
    THREAT_PATTERNS = [re.compile(pat, re.IGNORECASE) for pat in load_list("threat_patterns.txt")]

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        content = message.content
        lower = content.lower()

        # 1) Toxische Wörter (case-insensitive)
        for word in TOXIC_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", lower):
                await message.channel.send(
                    f"⚠️ Bitte unterlasse solche Ausdrücke, {message.author.mention}!"
                )
                return

        # 2) Drohungen (Regex-basiert)
        for pattern in THREAT_PATTERNS:
            if pattern.search(content):
                await message.channel.send(
                    f"🚨 Das klingt wie eine Drohung, {message.author.mention}! "
                    "Solches Verhalten ist hier nicht erlaubt."
                )
                return

        # Keine Probleme → normale Commands weiterverarbeiten
        await bot.process_commands(message)
