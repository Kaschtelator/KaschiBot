import aiohttp
import discord
import json
import os
import logging
from discord.ext import tasks, commands
import config
import asyncio
import html

logger = logging.getLogger(__name__)

LASTVID_PATH = "datenbank/lastVideos.json"
lastvids = []


async def read_lastvids():
    global lastvids
    if not os.path.exists(LASTVID_PATH):
        with open(LASTVID_PATH, "w") as f:
            json.dump([], f)
        lastvids = []
        logger.info("YouTube Videos Datenbank erstellt")
        return
    try:
        with open(LASTVID_PATH, "r") as f:
            lastvids = json.load(f)
        logger.info(f"YouTube Videos Datenbank geladen: {len(lastvids)} Einträge")
    except Exception as e:
        logger.error(f"Fehler beim Laden der YouTube Videos Datenbank: {e}")
        lastvids = []


async def save_lastvids():
    global lastvids
    try:
        with open(LASTVID_PATH, "w") as f:
            json.dump(lastvids, f, indent=2)
        logger.info("YouTube Videos Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der YouTube Videos Datenbank: {e}")


async def verify_youtube_channel():
    """Verifiziert, dass die Channel-ID und der Channel-Name übereinstimmen"""
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=snippet&id={config.YOUTUBE_CHANNEL_ID}&key={config.YT_API_KEY}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"YouTube Kanal-Verifikation fehlgeschlagen: {resp.status}")
                    return False, "API Error"

                data = await resp.json()
                if not data.get("items"):
                    logger.error("YouTube Kanal nicht gefunden!")
                    return False, "Channel nicht gefunden"

                channel_name = data["items"][0]["snippet"]["title"]
                logger.info(f"YouTube Kanal gefunden: {channel_name}")

                # Überprüfe, ob der Name dem erwarteten entspricht (aus config)
                if channel_name.lower() != config.YOUTUBE_CHANNEL_NAME.lower():
                    logger.error("❌ Kanal-Namen stimmen nicht überein!")
                    logger.error(f"   Erwartet: {config.YOUTUBE_CHANNEL_NAME}")
                    logger.error(f"   Gefunden: {channel_name}")
                    return (
                        False,
                        f"Kanal-Namen stimmen nicht überein! "
                        f"Erwartet: {config.YOUTUBE_CHANNEL_NAME}, Gefunden: {channel_name}"
                    )

                logger.info(f"✅ Kanal verifiziert: {channel_name}")
                return True, channel_name
    except Exception as e:
        logger.error(f"Fehler bei Kanal-Verifikation: {e}")
        return False, str(e)


def setup(bot: commands.Bot):
    asyncio.run(read_lastvids())

    # Kanal beim Start verifizieren (nur Log, kein Abbruch)
    asyncio.run(verify_youtube_channel())

    @tasks.loop(minutes=30)
    async def youtube_check():
        logger.info("Starte YouTube Check")

        # Verifiziere vor jedem Check
        is_valid, msg = await verify_youtube_channel()
        if not is_valid:
            logger.error(f"❌ YouTube Kanal-Verifikation fehlgeschlagen: {msg}")
            return

        channel = bot.get_channel(config.YOUTUBE_DISCORD_CHANNEL_ID)
        if channel:
            await check_youtube(bot, channel)
        else:
            logger.error("YouTube Discord-Channel nicht gefunden")

    @bot.command()
    async def youtube(ctx: commands.Context):
        """Prüft auf neue YouTube Videos"""
        logger.info(f"Manueller YouTube Check von {ctx.author}")

        # Verifiziere vor dem Check
        is_valid, msg = await verify_youtube_channel()
        if not is_valid:
            await ctx.send(f"❌ Kanal-Verifikation fehlgeschlagen: {msg}")
            return

        channel = bot.get_channel(config.YOUTUBE_DISCORD_CHANNEL_ID)
        if channel:
            await check_youtube(bot, channel)
            await ctx.send(f"✅ Check ausgeführt im YouTube-Channel: {channel.mention}")
        else:
            await ctx.send("YouTube-Channel nicht gefunden.")

    @bot.command(name="showposted")
    async def show_posted(ctx: commands.Context):
        """Listet alle bereits geposteten YouTube Videos auf"""
        if not lastvids:
            await ctx.send("Keine Videos in der Datenbank.")
            return

        lines = [f"Gepostete Videos ({len(lastvids)}):"]
        for v in lastvids:
            line = (
                f"{v.get('timestamp', 'unbekannt')} - "
                f"{v.get('author', 'unbekannt')}: "
                f"{v.get('title', 'kein Titel')} ({v.get('url', '')})"
            )
            lines.append(line)

        chunk_size = 1900
        msg = ""
        for line in lines:
            if len(msg) + len(line) + 1 > chunk_size:
                await ctx.send(msg)
                msg = ""
            msg += line + "\n"
        if msg:
            await ctx.send(msg)

    @bot.listen()
    async def on_ready():
        if not youtube_check.is_running():
            youtube_check.start()
        logger.info("YouTube Check Task gestartet (alle 30 Minuten)")


    async def check_youtube(bot: commands.Bot, channel: discord.TextChannel):
        global lastvids

        await read_lastvids()

        url = (
            "https://www.googleapis.com/youtube/v3/search?part=snippet"
            f"&channelId={config.YOUTUBE_CHANNEL_ID}"
            f"&maxResults=2&order=date&key={config.YT_API_KEY}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"YouTube API Error: {resp.status}")
                        return

                    data = await resp.json()
                    items = data.get("items", [])
                    logger.info(f"YouTube API Response: {len(items)} Videos gefunden")

                    new_videos_count = 0
                    for video in items:
                        vidid = video["id"].get("videoId")
                        if not vidid:
                            continue

                        # Basisdaten
                        title = html.unescape(video["snippet"]["title"])
                        video_url = f"https://youtube.com/watch?v={vidid}"
                        author = video["snippet"]["channelTitle"]
                        timestamp = video["snippet"]["publishedAt"]

                        # 1) Hard-Sicherheit: nur Videos posten, deren Kanalname passt
                        if author.lower() != config.YOUTUBE_CHANNEL_NAME.lower():
                            logger.warning(
                                "Ignoriere Video von fremdem Kanal: "
                                f"{author} - {title} ({video_url})"
                            )
                            continue

                        # 2) Nur neue Videos posten
                        if any(v["id"] == vidid for v in lastvids):
                            continue

                        msg = (
                            f"Hey Leute, **{author}** hat **\"{title}\"** hochgeladen: {video_url}"
                        )
                        await channel.send(msg)

                        lastvids.append(
                            {
                                "id": vidid,
                                "title": title,
                                "author": author,
                                "url": video_url,
                                "timestamp": timestamp,
                            }
                        )

                        new_videos_count += 1
                        logger.info(f"Neues YouTube Video gepostet: {title}")

                    await save_lastvids()

                    if new_videos_count == 0:
                        logger.info("Keine passenden neuen YouTube Videos gefunden")
                    else:
                        logger.info(
                            f"YouTube Check abgeschlossen: {new_videos_count} neue Videos gepostet"
                        )

        except Exception as e:
            logger.error(f"Fehler beim YouTube Check: {e}")
