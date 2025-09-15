import aiohttp
import discord
import json
import os
import logging
from discord.ext import tasks, commands
import config

logger = logging.getLogger(__name__)
LASTGAME_PATH = "datenbank/lastEpicGames.json"

def setup(bot):
    if not os.path.exists(LASTGAME_PATH):
        with open(LASTGAME_PATH, "w") as f:
            json.dump([], f)
        logger.info("Epic Games Datenbank erstellt")

    @tasks.loop(minutes=30)
    async def epic_check():
        logger.info("Starte Epic Games Check")
        channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
        if channel:
            await check_epic(channel)
        else:
            logger.error("Epic Games Channel nicht gefunden")

    @bot.command()
    async def epic(ctx):
        logger.info(f"Manueller Epic Games Check von {ctx.author}")
        await check_epic(ctx.channel)

    @bot.listen()
    async def on_ready():
        if not epic_check.is_running():
            epic_check.start()
            logger.info("Epic Games Check Task gestartet (alle 30 Minuten)")

async def check_epic(channel):
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=de-DE&country=DE&allowCountries=DE"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Epic API Error: {resp.status}")
                    return
                
                data = await resp.json()
                promotions = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
                
                if not promotions:
                    logger.info("Keine Epic Games Promotions gefunden")
                    return

        try:
            with open(LASTGAME_PATH, "r") as f:
                lastgames = json.load(f)
        except Exception:
            lastgames = []

        new_games_count = 0
        for game in promotions:
            if (game.get("promotions") and
                game["promotions"].get("promotionalOffers")):
                if any(g["id"] == game["id"] for g in lastgames):
                    continue
                
                title = game.get("title", "Unbekannt")
                pageSlug = (game.get("catalogNs", {}).get("mappings", [{}])[0].get("pageSlug")
                            or game.get("productSlug", ""))
                game_url = f"https://www.epicgames.com/store/de/p/{pageSlug}"
                game_image = (game.get("keyImages", [{}])[0].get("url")
                              or "https://cdn2.unrealengine.com/placeholder-image.jpg")
                
                price_info = game.get("price", {}).get("totalPrice", {}).get("fmtPrice", {})
                original_price_raw = price_info.get("originalPrice", "")
                
                if original_price_raw and original_price_raw not in ["€0.00", "0", "0 €", "0,00 €"]:
                    original_price = f"💰 {original_price_raw} **➜ Kostenlos!**"
                else:
                    original_price = "💰 **Kostenlos!**"
                
                embed = discord.Embed(
                    title=f"Kostenlos bei Epic Games: {title}",
                    description=f"Schnapp es dir 👉 [Epicgames.com]({game_url}) 👈",
                    color=0xffb700)
                embed.set_image(url=game_image)
                embed.add_field(name="Originalpreis", value=original_price)
                
                await channel.send("@everyone", embed=embed)
                lastgames.append({"id": game["id"]})
                new_games_count += 1
                logger.info(f"Neues kostenloses Epic Game gepostet: {title}")

        with open(LASTGAME_PATH, "w") as f:
            json.dump(lastgames, f)
            
        if new_games_count == 0:
            logger.info("Keine neuen Epic Games gefunden")
        else:
            logger.info(f"Epic Games Check abgeschlossen: {new_games_count} neue Spiele gefunden")

    except Exception as e:
        logger.error(f"Fehler beim Epic Games Check: {e}")
