import discord
import json
import os
import secrets
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands

DICE_DB_PATH = "datenbank/user_dice.json"

def ensure_json(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_json(path):
    ensure_json(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def setup(bot: commands.Bot):
    ensure_json(DICE_DB_PATH)

    @bot.command(name="würfel")
    async def wuerfel(ctx: commands.Context):
        """Würfelt mit dem zuletzt gewählten Würfel (Cooldown 1h)."""
        user_id = str(ctx.author.id)
        user_data = load_json(DICE_DB_PATH)
        now = datetime.utcnow()
        entry = user_data.get(user_id)

        # Cooldown aktiv?
        if entry:
            last_time = datetime.fromisoformat(entry["timestamp"])
            if now - last_time < timedelta(hours=1):
                sides = entry["sides"]
                result = secrets.randbelow(sides) + 1
                # Nur einmal Hinweis anzeigen
                if not entry.get("notified", False):
                    await ctx.send(f"🎲 Du würfelst einen d{sides} und bekommst **{result}**\n💡 Hinweis: Für die nächste Stunde wird derselbe Würfel verwendet. Tippe `!neuerwürfel` um eine neue Auswahl zu treffen.")
                    entry["notified"] = True
                    save_json(DICE_DB_PATH, user_data)
                else:
                    await ctx.send(f"🎲 Du würfelst einen d{sides} und bekommst **{result}**")
                return

        # Neue Auswahl oder Cooldown abgelaufen
        await ctx.send(
            "Welchen Würfel möchtest du verwenden? Gib die Anzahl der Seiten ein "
            "(z.B. 6 für d6 oder 20 für d20)."
        )

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Zeit abgelaufen. Probiere es bitte später noch einmal.")
            return

        content = msg.content.lower().lstrip("d")
        if not content.isdigit():
            await ctx.send("Ungültige Eingabe. Bitte eine Zahl eingeben.")
            return

        sides = int(content)
        valid = {4, 6, 8, 10, 12, 20, 100}
        if sides not in valid:
            await ctx.send("Ungültiger Würfeltyp. Erlaubt: 4, 6, 8, 10, 12, 20, 100.")
            return

        # Neue Auswahl: Timestamp zurücksetzen und notified auf False
        user_data[user_id] = {
            "sides": sides,
            "timestamp": now.isoformat(),
            "notified": False
        }
        save_json(DICE_DB_PATH, user_data)

        result = secrets.randbelow(sides) + 1
        await ctx.send(
            f"🎲 Du würfelst einen d{sides} und bekommst **{result}**\n"
            "💡 Hinweis: Für die nächste Stunde wird derselbe Würfel verwendet. "
            "Tippe `!neuerwürfel` um eine neue Auswahl zu treffen."
        )

    @bot.command(name="neuerwürfel")
    async def neuer_wuerfel(ctx: commands.Context):
        """Löscht deine gespeicherte Würfelauswahl."""
        user_id = str(ctx.author.id)
        user_data = load_json(DICE_DB_PATH)
        if user_id in user_data:
            del user_data[user_id]
            save_json(DICE_DB_PATH, user_data)
            await ctx.send("Deine Würfelauswahl wurde zurückgesetzt. Tippe `!würfel` um erneut auszuwählen.")
        else:
            await ctx.send("Keine gespeicherte Würfelauswahl vorhanden. Tippe `!würfel` um auszuwählen.")
