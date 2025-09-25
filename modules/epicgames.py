import aiohttp
import discord
import json
import os
import logging
from discord.ext import tasks, commands
import config
import asyncio


logger = logging.getLogger(__name__)
LASTGAME_PATH = "datenbank/lastEpicGames.json"
lastgames = []


async def read_last_games():
    global lastgames
    if not os.path.exists(LASTGAME_PATH):
        with open(LASTGAME_PATH, "w") as f:
            json.dump([], f)
        lastgames = []
        logger.info("Epic Games Datenbank erstellt")
        return


    try:
        with open(LASTGAME_PATH, "r") as f:
            lastgames = json.load(f)
        logger.info(f"Epic Games Datenbank geladen: {len(lastgames)} Einträge")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Epic Games Datenbank: {e}")
        lastgames = []


async def save_last_games():
    global lastgames
    try:
        with open(LASTGAME_PATH, "w") as f:
            json.dump(lastgames, f)
        logger.info("Epic Games Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Epic Games Datenbank: {e}")


async def check_epic(channel, force_chat_output=False, triggered_by="Unbekannt"):
    global lastgames
    if not lastgames:
        await read_last_games()
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=de-DE&country=DE&allowCountries=DE"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Epic API Error: {resp.status} (Ausgelöst von: {triggered_by})")
                    if force_chat_output:
                        await channel.send("🚫 Fehler beim Abrufen der Epic Games-Daten.")
                    return
                
                data = await resp.json()
                promotions = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
                
                if not promotions:
                    logger.info(f"Keine Epic Games Promotions gefunden (Ausgelöst von: {triggered_by})")
                    if force_chat_output:
                        await channel.send("ℹ️ Zurzeit sind keine Gratis-Spiele im Epic Games Store verfügbar.")
                    return


        new_games_count = 0
        for game in promotions:
            if (game.get("promotions") and game["promotions"].get("promotionalOffers")):
                if any(g["id"] == game["id"] for g in lastgames):
                    continue
                
                title = game.get("title", "Unbekannt")
                pageSlug = (game.get("catalogNs", {}).get("mappings", [{}])[0].get("pageSlug") or game.get("productSlug", ""))
                game_url = f"https://www.epicgames.com/store/de/p/{pageSlug}"
                game_image = (game.get("keyImages", [{}])[0].get("url") or "https://cdn2.unrealengine.com/placeholder-image.jpg")
                
                price_info = game.get("price", {}).get("totalPrice", {}).get("fmtPrice", {})
                original_price_raw = price_info.get("originalPrice", "")
                
                if original_price_raw and original_price_raw not in ["€0.00", "0", "0 €", "0,00 €"]:
                    original_price = f"💰 {original_price_raw} **→ Kostenlos!**"
                else:
                    original_price = "💰 **Kostenlos!**"
                
                embed = discord.Embed(title=f"Kostenlos bei Epic Games: {title}",
                                      description=f"Schnapp es dir 👉 [Epicgames.com]({game_url}) 👈",
                                      color=0xffb700)
                embed.set_image(url=game_image)
                embed.add_field(name="Originalpreis", value=original_price)
                
                if force_chat_output:
                    await channel.send("@everyone", embed=embed)
                else:
                    post_channel = channel.guild.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
                    if post_channel:
                        await post_channel.send("@everyone", embed=embed)


                lastgames.append({"id": game["id"]})
                new_games_count += 1
                logger.info(f"Neues kostenloses Epic Game gepostet: {title} (Ausgelöst von: {triggered_by})")


        await save_last_games()
        
        if new_games_count == 0:
            logger.info(f"Keine neuen Epic Games gefunden (Ausgelöst von: {triggered_by})")
            if force_chat_output:
                await channel.send("✔️ Keine neuen kostenlosen Spiele entdeckt.")
        else:
            logger.info(f"Epic Games Check abgeschlossen: {new_games_count} neue Spiele gefunden (Ausgelöst von: {triggered_by})")
            if force_chat_output:
                await channel.send(f"✅ Es wurden {new_games_count} neue kostenlose Spiele gepostet!")


    except Exception as e:
        logger.error(f"Fehler beim Epic Games Check: {e} (Ausgelöst von: {triggered_by})")
        if force_chat_output:
            await channel.send(f"⛔ Fehler beim Epic Games-Check: {e}")


def setup(bot):
    asyncio.run(read_last_games())  # sicheres synchrones Laden (keine EventLoop Fehler)

    @tasks.loop(minutes=30)
    async def epic_check():
        logger.info("Starte automatischen Epic Games Check (Task)")
        channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
        if channel:
            await check_epic(channel, force_chat_output=False, triggered_by="Auto-Task")
        else:
            logger.error("Epic Games Channel nicht gefunden (Task)")

    @bot.command()
    async def epic(ctx):
        logger.info(f"Manueller Epic Games Check durch {ctx.author}")
        await ctx.send("🔎 Suche nach neuen kostenlosen Spielen im Epic Games Store ...")
        await check_epic(ctx.channel, force_chat_output=True, triggered_by=ctx.author)

    @bot.listen()
    async def on_ready():
        if not epic_check.is_running():
            epic_check.start()
            logger.info("Epic Games Check Task gestartet (alle 30 Minuten)")
