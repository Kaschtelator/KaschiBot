import aiohttp
import asyncio
import json
import os
import re
import logging
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from discord import Embed
import config


logger = logging.getLogger(__name__)
DB_PATH = "datenbank/lastGogGames.json"
last_giveaways = []


async def read_last_giveaways():
    global last_giveaways
    if not os.path.exists(DB_PATH):
        last_giveaways = []
        await save_last_giveaways()
        logger.info("GOG Giveaway Datenbank erstellt")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            last_giveaways = json.load(f)
        for g in last_giveaways:
            g["productId"] = str(g["productId"])
        logger.info(f"GOG Giveaway Datenbank geladen: {len(last_giveaways)} Eintraege")
    except Exception as e:
        logger.error(f"Fehler beim Laden der GOG Giveaway Datenbank: {e}")
        last_giveaways = []


async def save_last_giveaways():
    global last_giveaways
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(last_giveaways, f, indent=2)
        logger.info("GOG Giveaway Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der GOG Giveaway Datenbank: {e}")


def parse_giveaway_from_html(html_text):
    """Extrahiert das aktuelle Giveaway aus dem eingebetteten JSON-State von gog.com"""
    m = re.search(
        r'<script id="gogcom-store-state" type="application/json">(.*?)</script>',
        html_text, re.S
    )
    if not m:
        return None

    try:
        data = json.loads(m.group(1))
    except Exception as e:
        logger.warning(f"Fehler beim Parsen des GOG State-JSON: {e}")
        return None

    for value in data.values():
        if not isinstance(value, dict):
            continue
        props = value.get("body", {}).get("properties")
        if not isinstance(props, dict):
            continue
        product = props.get("product")
        end_date = props.get("endDate")
        if product and end_date:
            price = product.get("price") or {}
            return {
                "productId": str(product.get("id")),
                "title": product.get("title", "Unbekannt"),
                "slug": product.get("slug"),
                "image": product.get("coverHorizontal") or product.get("galaxyBackgroundImage"),
                "endDate": end_date,
                "originalPrice": price.get("base"),
            }
    return None


def format_end_date(end_date_str):
    """Formatiert ISO-Datum lesbar, z. B. 10.09.2026, 16:00 Uhr"""
    try:
        end_dt = datetime.fromisoformat(end_date_str)
        return end_dt.strftime("%d.%m.%Y, %H:%M Uhr")
    except Exception:
        return end_date_str


async def fetch_gog_giveaway(bot, force_chat_output=False, context_channel=None, triggered_by="Task"):
    global last_giveaways
    logger.info(f"Suche nach GOG Giveaways... (Ausgel\u00f6st von: {triggered_by})")

    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        url = "https://www.gog.com/en/"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"GOG Store Error: {resp.status}")
                    if force_chat_output and context_channel:
                        await context_channel.send("Fehler beim Abrufen der GOG-Daten.")
                    return

                html_text = await resp.text()
                if not html_text:
                    logger.warning("Keine HTML-Daten von GOG erhalten")
                    if force_chat_output and context_channel:
                        await context_channel.send("Keine Daten von GOG erhalten.")
                    return

            if force_chat_output and context_channel:
                await context_channel.send("Suche nach neuen GOG Giveaways ...")

            giveaway = parse_giveaway_from_html(html_text)

            if not giveaway:
                logger.info("Kein aktives GOG Giveaway gefunden")
                if force_chat_output and context_channel:
                    await context_channel.send("Aktuell kein GOG Giveaway aktiv.")
                return

            product_id = giveaway["productId"]

            # Duplicate-Check
            already_posted = next((g for g in last_giveaways if str(g["productId"]) == product_id), None)
            if already_posted:
                posted_date = datetime.fromisoformat(already_posted["date"])
                if datetime.utcnow() - posted_date < timedelta(days=14):
                    logger.debug(f"\u00dcbersprungen (bereits gepostet): {product_id}")
                    if force_chat_output and context_channel:
                        await context_channel.send("Kein neues GOG Giveaway (bereits gepostet).")
                    return

            post_channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
            if not post_channel:
                logger.error("Freegames Channel aus config nicht gefunden")
                if force_chat_output and context_channel:
                    await context_channel.send("Fehler: Freigabe-Channel nicht gefunden.")
                return

            link = f"https://www.gog.com/en/game/{giveaway['slug']}" if giveaway.get("slug") else "https://www.gog.com/en/#giveaway"

            if giveaway.get("originalPrice"):
                price_text = f"\U0001F4B0 {giveaway['originalPrice']} \u2192 Kostenlos!"
            else:
                price_text = "\U0001F4B0 Kostenlos!"

            end_readable = format_end_date(giveaway["endDate"])

            embed = Embed(
                title=f"Kostenlos bei GOG: {giveaway['title']}",
                description=f"Schnapp es dir \U0001F449 [GOG Store]({link}) \U0001F448",
                color=0x6E1D72
            )
            embed.add_field(name="Originalpreis", value=price_text)
            embed.add_field(name="Verf\u00fcgbar bis", value=end_readable, inline=False)
            if giveaway.get("image"):
                embed.set_image(url=giveaway["image"])
            embed.timestamp = datetime.utcnow()

            await post_channel.send("@everyone", embed=embed)

            logger.info(f"Neues GOG Giveaway gepostet: {giveaway['title']} (Ausgel\u00f6st von: {triggered_by})")

            last_giveaways.append({
                "productId": product_id,
                "title": giveaway["title"],
                "date": datetime.utcnow().isoformat()
            })

            if len(last_giveaways) > 50:
                last_giveaways = last_giveaways[-50:]

            await save_last_giveaways()

            if force_chat_output and context_channel:
                await context_channel.send(f"GOG Giveaway gepostet: {giveaway['title']}")

            logger.info(f"GOG Check abgeschlossen (Ausgel\u00f6st von: {triggered_by})")

        except Exception as e:
            logger.error(f"Fehler beim GOG Check: {e}")
            if force_chat_output and context_channel:
                await context_channel.send(f"Fehler beim GOG-Check: {e}")


async def check_gog_giveaway(bot, force_chat_output=False, context_channel=None, triggered_by="Task"):
    await read_last_giveaways()
    await fetch_gog_giveaway(bot, force_chat_output, context_channel, triggered_by)


def setup(bot):

    @tasks.loop(hours=1)
    async def gog_check():
        logger.info("Starte GOG Giveaway Check (Task)")
        await check_gog_giveaway(bot, force_chat_output=False, triggered_by="Auto-Task")

    @bot.command()
    async def gogfree(ctx):
        """Prueft auf neues GOG Giveaway"""
        logger.info(f"Manueller GOG Check von {ctx.author}")
        try:
            await check_gog_giveaway(bot, force_chat_output=True, context_channel=ctx.channel, triggered_by=ctx.author)
        except Exception as e:
            await ctx.send(f"Fehler beim GOG-Check: {e}")

    @bot.listen()
    async def on_ready():
        if not gog_check.is_running():
            gog_check.start()
            logger.info("GOG Giveaway Check Task gestartet (alle 60 Minuten)")