import discord
import json
import os
from discord.ext import commands

STATUS_PATH = "datenbank/status.json"

def load_status():
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    if not os.path.exists(STATUS_PATH):
        default = {"name": "Status nicht gesetzt", "debugging": False, "channel": False, "url": ""}
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        return default
    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        default = {"name": "Status nicht gesetzt", "debugging": False, "channel": False, "url": ""}
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        return default

def save_status(status_data):
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

def setup(bot):
    print("🔧 Status-Modul wird geladen...")

    @bot.listen("on_ready")
    async def restore_status():
        """Stellt den gespeicherten Status beim Bot-Start wieder her"""
        status_data = load_status()
        if status_data.get("name") and status_data.get("url"):
            try:
                await bot.change_presence(
                    activity=discord.Streaming(
                        name=status_data["name"],
                        url=status_data["url"]
                    )
                )
                print(f"✅ Status wiederhergestellt: {status_data['name']} | {status_data['url']}")
            except Exception as e:
                print(f"❌ Fehler beim Wiederherstellen des Status: {e}")

    @bot.listen("on_message")
    async def status_listener(message):
        if message.author.bot:
            return

        if message.content.startswith("!BotKaschiCommand;"):
            print(f"🎯 BotKaschiCommand erkannt von {message.author}")
            print(f"📝 Rohe Message: '{message.content}'")

            args_part = message.content[len("!BotKaschiCommand;"):]
            parts = [part.strip() for part in args_part.split(";")]
            print(f"📝 Parts: {parts}")

            if len(parts) < 2:
                await message.channel.send(
                    "❌ Ungültiges Format. Bitte `!BotKaschiCommand;Name;URL` verwenden.\n"
                    "📝 **Beispiel:** `!BotKaschiCommand; Vogelfrey - Alle sagen das; https://www.youtube.com/watch?v=xyz`"
                )
                return

            name = parts[0]
            url = parts[1]

            original_url = url
            if url.startswith("[") and "](" in url and url.endswith(")"):
                url = url.split("](")[1][:-1]

            print(f"🎵 Name: '{name}'")
            print(f"🔗 Original: '{original_url}'")
            print(f"🔗 Bereinigt: '{url}'")

            try:
                status_data = load_status()
                status_data["name"] = name
                status_data["url"] = url
                save_status(status_data)

                await bot.change_presence(activity=discord.Streaming(name=name, url=url))

                await message.channel.send(
                    f"✅ **Status erfolgreich aktualisiert:**\n"
                    f"🎵 **Spielt:** {name}\n"
                    f"🔗 **URL:** {url}\n"
                    f"📺 **Streaming-Modus aktiviert**"
                )

                print(f"✅ Status gesetzt: {name} | URL: {url}")

            except Exception as e:
                error_msg = f"❌ Fehler beim Setzen des Status: {e}"
                await message.channel.send(error_msg)
                print(f"❌ Fehler: {e}")

    print("✅ Status-Modul erfolgreich geladen!")
