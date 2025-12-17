# config.py

"""
Konfigurationsdatei für Kaschibot.
Lege diese Datei im Projektverzeichnis ab und fülle die Werte.

Beispiel:
TOKEN = "DEIN_DISCORD_BOT_TOKEN"
YT_API_KEY = "DEIN_GOOGLE_API_KEY"
YOUTUBE_CHANNEL_ID = "UCxxxxxxxxxxxxxxx"
YOUTUBE_DISCORD_CHANNEL_ID = 123456789012345678
FREEGAMES_DISCORD_CHANNEL_ID = 123456789012345678
BDAY_DISCORD_CHANNEL_ID = 123456789012345678
CHECKCHANNEL_ID = 123456789012345678
"""

import os
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

# Bot-Token (Discord)
TOKEN = os.getenv("DISCORD_TOKEN")

# YouTube API-Schlüssel
YT_API_KEY = os.getenv("YT_API_KEY")

# YouTube Channels
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
YOUTUBE_CHANNEL_NAME = os.getenv("YOUTUBE_CHANNEL_NAME")
YOUTUBE_DISCORD_CHANNEL_ID = int(os.getenv("YOUTUBE_DISCORD_CHANNEL_ID"))

# Discord-Kanäle
FREEGAMES_DISCORD_CHANNEL_ID = int(os.getenv("FREEGAMES_DISCORD_CHANNEL_ID"))
BDAY_DISCORD_CHANNEL_ID = int(os.getenv("BDAY_DISCORD_CHANNEL_ID"))
CHECKCHANNEL_ID = int(os.getenv("CHECKCHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
GOODBYE_CHANNEL_ID = int(os.getenv("GOODBYE_CHANNEL_ID"))
