import aiohttp
import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from discord import Embed
import config


logger = logging.getLogger(__name__)
DB_PATH = "datenbank/lastSteamGames.json"
last_games = []


async def read_last_games():
    global last_games
    if not os.path.exists(DB_PATH):
        last_games = []
        await save_last_games()
        logger.info("Steam Games Datenbank erstellt")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            last_games = json.load(f)
        logger.info(f"Steam Games Datenbank geladen: {len(last_games)} Einträge")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Steam Games Datenbank: {e}")
        last_games = []


async def save_last_games():
    global last_games
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(last_games, f, indent=2)
        logger.info("Steam Games Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Steam Games Datenbank: {e}")


async def fetch_free_steam_games(bot, force_chat_output=False, context_channel=None, triggered_by="Task"):
    global last_games
    logger.info(f"Suche nach kostenlosen Steam-Spielen... (Ausgelöst von: {triggered_by})")

    # Neu einlesen für Live-Update
    await read_last_games()

    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        url = "https://store.steampowered.com/search/?maxprice=free&category1=998%2C996&specials=1&ndl=1"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Steam Store Error: {resp.status}")
                    if force_chat_output and context_channel:
                        await context_channel.send("🚫 Fehler beim Abrufen der Steam-Daten.")
                    return

                html_text = await resp.text()
                if not html_text:
                    logger.warning("Keine HTML-Daten von Steam Store erhalten")
                    if force_chat_output and context_channel:
                        await context_channel.send("⚠️ Keine Daten vom Steam Store erhalten.")
                    return

            import re
            appid_matches = re.findall(r'data-ds-appid="(\d+)"', html_text)
            if not appid_matches:
                logger.info("Keine Steam AppIDs gefunden")
                if force_chat_output and context_channel:
                    await context_channel.send("ℹ️ Keine kostenlosen Steam-Games gefunden.")
                return

            unique_appids = list(set(appid_matches))
            logger.info(f"{len(unique_appids)} Steam Apps gefunden")

            game_info_tasks = []
            for appid in unique_appids:
                api_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                game_info_tasks.append(session.get(api_url))

            responses = await asyncio.gather(*game_info_tasks, return_exceptions=True)

            post_channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
            if not post_channel:
                logger.error("Steam Freegames Channel aus config nicht gefunden")
                if force_chat_output and context_channel:
                    await context_channel.send("🚫 Fehler: Freigabe-Channel nicht gefunden, Spiele können nicht gepostet werden.")
                return

            if force_chat_output and context_channel:
                await context_channel.send("🔎 Suche nach neuen kostenlosen Spielen auf Steam ...")

            new_games_count = 0
            for response in responses:
                if isinstance(response, Exception):
                    logger.warning(f"Fehler bei Steam API-Abfrage: {response}")
                    continue

                try:
                    data = await response.json()
                except Exception as e:
                    logger.warning(f"Fehler beim Steam JSON parsen: {e}")
                    continue

                appid = list(data.keys())[0]
                game_data = data[appid].get("data")
                if not game_data:
                    continue

                already_posted = next((g for g in last_games if g["appId"] == appid), None)
                if already_posted:
                    posted_date = datetime.fromisoformat(already_posted["date"])
                    if datetime.utcnow() - posted_date < timedelta(days=90):
                        continue

                title = game_data.get("name", "Unbekannt")
                image = game_data.get("header_image", "")
                link = f"https://store.steampowered.com/app/{appid}"
                price_overview = game_data.get("price_overview")

                if price_overview and price_overview.get("initial", 0) > 0:
                    original_price_euro = price_overview["initial"] / 100
                    price_text = f"💰 {original_price_euro:.2f}€ **➜ Kostenlos!**"
                else:
                    price_text = "💰 **Kostenlos!**"

                embed = Embed(
                    title=f"Neues kostenloses Spiel auf Steam: {title}",
                    description=f"Schnapp es dir 👉 [Steam Store]({link}) 👈",
                    color=0x66C0F4)
                embed.add_field(name="Originalpreis", value=price_text)
                embed.set_image(url=image)
                embed.timestamp = datetime.utcnow()

                await post_channel.send("@everyone", embed=embed)

                logger.info(f"Neues kostenloses Steam Game gepostet: {title} (Ausgelöst von: {triggered_by})")
                new_games_count += 1

                last_games.append({"appId": appid, "title": title, "date": datetime.utcnow().isoformat()})

            if len(last_games) > 100:
                last_games = last_games[-100:]

            await save_last_games()

            if force_chat_output and context_channel:
                if new_games_count == 0:
                    await context_channel.send("✔️ Keine neuen kostenlosen Steam-Spiele entdeckt.")
                else:
                    await context_channel.send(f"✅ Es wurden {new_games_count} neue Steam-Spiele gepostet!")

            logger.info(f"Steam Check abgeschlossen: {new_games_count} neue Spiele gefunden (Ausgelöst von: {triggered_by})")

        except Exception as e:
            logger.error(f"Fehler beim Steam Check: {e}")
            if force_chat_output and context_channel:
                await context_channel.send(f"⛔ Fehler beim Steam-Check: {e}")


async def check_steam_free_games(bot, force_chat_output=False, context_channel=None, triggered_by="Task"):
    if not last_games:
        await read_last_games()
    await fetch_free_steam_games(bot, force_chat_output, context_channel, triggered_by)


def setup(bot):
    asyncio.run(read_last_games())  # robustes synchrones Laden vor Task


    @tasks.loop(hours=1)
    async def steam_check():
        logger.info("Starte Steam Free Games Check (Task)")
        await check_steam_free_games(bot, force_chat_output=False, triggered_by="Auto-Task")


    @bot.command()
    async def steamfree(ctx):
        logger.info(f"Manueller Steam Check von {ctx.author}")
        try:
            await check_steam_free_games(bot, force_chat_output=True, context_channel=ctx.channel, triggered_by=ctx.author)
        except Exception as e:
            await ctx.send(f"Fehler beim Steam-Check: {e}")


    @bot.listen()
    async def on_ready():
        if not steam_check.is_running():
            steam_check.start()
            logger.info("Steam Check Task gestartet (alle 60 Minuten)")
