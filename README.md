# 🤖 Kaschibot

Ein umfassender Discord Bot für Community-Management mit automatischen Benachrichtigungen, Moderation und Event-Tracking.

![Discord](https://img.shields.io/badge/Discord-Bot-blue?logo=discord)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🛡️ **Moderation**
- Automatische Erkennung von Schimpfwörtern und toxischen Begriffen
- Drohungserkennung mit Regex-Mustern  
- Anpassbare Wortlisten über Textdateien
- Sofortige Warnungen bei Regelverstößen

### 🎮 **Gaming Benachrichtigungen**
- **Epic Games**: Automatische Posts bei kostenlosen Spielen (alle 30 Min)
- **Steam**: Free Games Überwachung mit 90-Tage Cooldown (stündlich)
- Embed-Nachrichten mit Bildern und Preisvergleichen
- @everyone Mentions für wichtige Deals

### 📺 **YouTube Integration**
- Channel-Überwachung für neue Videos (alle 10 Min)
- Automatische Posts mit Video-Links
- Konfigurierbare Channel-IDs

### 🎂 **Geburtstags-System**
- Geburtstage hinzufügen/verwalten (`!addgeburtstag Name TT-MM`)
- Automatische tägliche Glückwünsche um 9:00 Uhr
- Duplikat-Schutz und Datumsvalidierung
- Übersichtliche Geburtstags-Checks

### 👋 **Willkommens-System**
- Zufällige Begrüßungs-/Abschiedsnachrichten
- Gothic-inspirierte Texte aus JSON-Dateien
- Member Join/Leave Events

### 🔄 **Hot-Reload**
- Automatisches Neuladen bei Code-Änderungen
- Keine Bot-Neustarts für Updates
- Watchdog-basierte Dateiüberwachung

## 📦 Installation

### Voraussetzungen
- Python 3.8 oder höher
- Discord Bot Token
- Optional: YouTube Data API Key

### Setup

1. **Repository klonen**
git clone https://github.com/DeinUsername/kaschibot.git
cd kaschibot


2. **Dependencies installieren**
pip install -r requirements.txt

3. **Datenbank-Ordner erstellen**
mkdir datenbank

4. **Konfiguration anpassen**
cp config.py config_real.py

5. **Bot starten**
python kaschibot.py

## ⚙️ Konfiguration

Bearbeite `config.py` mit deinen Daten:
Discord Bot Token
TOKEN = "DEIN_DISCORD_BOT_TOKEN"

YouTube API (optional)
YT_API_KEY = "DEIN_YOUTUBE_API_KEY"
YOUTUBE_CHANNEL_ID = "UCxxxxxxxxxxxxxxxxx"

Discord Channel IDs
YOUTUBE_DISCORD_CHANNEL_ID = 123456789012345678
FREEGAMES_DISCORD_CHANNEL_ID = 123456789012345678
BDAY_DISCORD_CHANNEL_ID = 123456789012345678
WELCOME_CHANNEL_ID = 123456789012345678
GOODBYE_CHANNEL_ID = 123456789012345678
CHECKCHANNEL_ID = 123456789012345678

### Discord Bot Setup

1. Gehe zu https://discord.com/developers/applications
2. **New Application** → Bot Name eingeben
3. **Bot** → **Add Bot**
4. **Token** kopieren → in `config.py` einfügen
5. **OAuth2** → **URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Administrator` (oder spezifische Rechte)
6. Bot zum Server hinzufügen

## 📁 Datei-Struktur

kaschibot/
├── kaschibot.py # Hauptbot mit Hot-Reload
├── config.py # Konfiguration (Template)
├── requirements.txt # Python Dependencies
├── modules/ # Bot Module
│ ├── moderation.py # Chat-Moderation
│ ├── greetings.py # Willkommen/Abschied
│ ├── birthday.py # Geburtstags-System
│ ├── youtube.py # YouTube Notifications
│ ├── epicgames.py # Epic Games Tracker
│ └── steamgames.py # Steam Free Games
└── datenbank/ # Datenbank-Dateien
├── bad_words.txt # Schimpfwörter-Liste
├── threat_patterns.txt # Drohungs-Regex
├── Willkommen.json # Begrüßungstexte
├── Wiedersehen.json # Abschiedstexte
├── birthdays.json # Geburtstage (auto-created)
├── lastEpicGames.json # Epic Games Cache (auto-created)
├── lastVideos.json # YouTube Cache (auto-created)
└── lastSteamGames.json # Steam Cache (auto-created)


## 🎯 Commands

| Command | Beschreibung | Beispiel |
|---------|--------------|----------|
| `!addgeburtstag` | Geburtstag hinzufügen | `!addgeburtstag Max 15-03` |
| `!checkgeburtstag` | Geburtstage anzeigen | `!checkgeburtstag` |
| `!youtube` | Manueller YouTube Check | `!youtube` |
| `!epic` | Manueller Epic Games Check | `!epic` |
| `!steamfree` | Manueller Steam Check | `!steamfree` |

