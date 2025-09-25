import discord
import json
import os
from discord.ext import commands

STATUS_PATH = "datenbank/status.json"

def load_status():
    if not os.path.exists(STATUS_PATH):
        default = {"name": "Status nicht gesetzt", "debugging": False, "channel": False, "url": ""}
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        return default
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_status(status_data):
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

def setup(bot):
    @bot.command(name="BotKaschiCommand")
    async def botkaschicommand(ctx, *, args=None):
        """
        Ändert den Status des Bots.
        Command Format:
        !BotKaschiCommand; Name; URL
        Beispiel:
        !BotKaschiCommand; Mr. Hurley & Die Pulveraffen - Die Nacht ist noch jung; https://www.youtube.com/watch?v=3dd9dvbgmG0
        """
        if not args:
            await ctx.send("Bitte gib Argumente im Format `!BotKaschiCommand; Name; URL` an.")
            return

        parts = [part.strip() for part in args.split(";")]
        if len(parts) < 2:
            await ctx.send("Ungültiges Format. Bitte `!BotKaschiCommand; Name; URL` verwenden.")
            return

        name = parts[0]
        url = parts[1]

        status_data = load_status()
        status_data["name"] = name
        status_data["url"] = url

        save_status(status_data)

        await bot.change_presence(activity=discord.Streaming(name=name, url=url))

        await ctx.send(f"Status erfolgreich aktualisiert:\nName: {name}\nURL: {url}")

    @bot.event
    async def on_ready():
        status_data = load_status()
        try:
            await bot.change_presence(activity=discord.Streaming(
                name=status_data.get("name", "Status nicht gesetzt"),
                url=status_data.get("url", "")
            ))
        except Exception as e:
            print(f"Fehler beim automatischen Setzen des Status beim Start: {e}")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            # Ignoriere unbekannte Befehle still, keine Fehlermeldung
            return
        raise error
