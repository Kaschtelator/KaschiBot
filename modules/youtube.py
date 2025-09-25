import aiohttp
import discord
import json
import os
import logging
from discord.ext import tasks, commands
import config
import asyncio

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
            json.dump(lastvids, f)
        logger.info("YouTube Videos Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der YouTube Videos Datenbank: {e}")

def setup(bot):
    asyncio.run(read_lastvids())

    @tasks.loop(minutes=10)
    async def youtube_check():
        logger.info("Starte YouTube Check")
        channel = bot.get_channel(config.YOUTUBE_DISCORD_CHANNEL_ID)
        if channel:
            await check_youtube(bot, channel)
        else:
            logger.error("YouTube Channel nicht gefunden")

    @bot.command()
    async def youtube(ctx):
        logger.info(f"Manueller YouTube Check von {ctx.author}")
        channel = bot.get_channel(config.YOUTUBE_DISCORD_CHANNEL_ID)
        if channel:
            await check_youtube(bot, channel)
            await ctx.send(f"Check ausgeführt im YouTube-Channel: {channel.mention}")
        else:
            await ctx.send("YouTube-Channel nicht gefunden.")

    @bot.listen()
    async def on_ready():
        if not youtube_check.is_running():
            youtube_check.start()
            logger.info("YouTube Check Task gestartet (alle 10 Minuten)")

async def check_youtube(bot, channel):
    global lastvids
    if not lastvids:
        await read_lastvids()
    url = (f"https://www.googleapis.com/youtube/v3/search?part=snippet"
           f"&channelId={config.YOUTUBE_CHANNEL_ID}&maxResults=2&order=date&key={config.YT_API_KEY}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"YouTube API Error: {resp.status}")
                    return
                
                data = await resp.json()
                logger.info(f"YouTube API Response: {len(data.get('items', []))} Videos gefunden")

        new_videos_count = 0
        for video in data.get("items", []):
            vidid = video["id"].get("videoId")
            if not vidid:
                continue

            if not any(v["id"] == vidid for v in lastvids):
                title = video["snippet"]["title"]
                video_url = f"https://youtube.com/watch?v={vidid}"
                author = video["snippet"]["channelTitle"]
                msg = f"Hey Leute, **{author}** hat **\"{title}\"** hochgeladen: {video_url}"

                await channel.send(msg)
                lastvids.append({"id": vidid, "timestamp": video["snippet"]["publishedAt"]})
                new_videos_count += 1
                logger.info(f"Neues YouTube Video gepostet: {title}")

                await save_lastvids()
        
        if new_videos_count == 0:
            logger.info("Keine neuen YouTube Videos gefunden")
        else:
            logger.info(f"YouTube Check abgeschlossen: {new_videos_count} neue Videos gefunden")

    except Exception as e:
        logger.error(f"Fehler beim YouTube Check: {e}")
