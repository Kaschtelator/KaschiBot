# ƘƛƧƇӇƖƁƠƬ

Ein umfassender Discord Bot für Community-Management mit automatischen Benachrichtigungen, Moderation und Event-Tracking.

![Discord](https://img.shields.io/badge/Discord-Bot-blue?logo=discord)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

##  Features

###  **Moderation**
- Automatische Erkennung von Schimpfwörtern und toxischen Begriffen
- Drohungserkennung mit Regex-Mustern  
- Anpassbare Wortlisten über Textdateien
- Sofortige Warnungen bei Regelverstößen

###  **Gaming Benachrichtigungen**
- **Epic Games**: Automatische Posts bei kostenlosen Spielen (alle 30 Min)
- **Steam**: Free Games Überwachung mit 90-Tage Cooldown (stündlich)
- Embed-Nachrichten mit Bildern und Preisvergleichen
- @everyone Mentions für wichtige Deals

###  **YouTube Integration**
- Channel-Überwachung für neue Videos (alle 10 Min)
- Automatische Posts mit Video-Links
- Konfigurierbare Channel-IDs

###  **Geburtstags-System**
- Geburtstage hinzufügen/verwalten (`!addgeburtstag Name TT-MM`)
- Automatische tägliche Glückwünsche um 9:00 Uhr
- Duplikat-Schutz und Datumsvalidierung
- Übersichtliche Geburtstags-Checks

###  **Willkommens-System**
- Zufällige Begrüßungs-/Abschiedsnachrichten
- Gothic-inspirierte Texte aus JSON-Dateien
- Member Join/Leave Events

###  **Hot-Reload**
- Automatisches Neuladen bei Code-Änderungen
- Keine Bot-Neustarts für Updates
- Watchdog-basierte Dateiüberwachung

##  Installation

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

##  Konfiguration

Bearbeite `.env` mit deinen Daten.

### Discord Bot Setup

1. Gehe zu https://discord.com/developers/applications
2. **New Application** → Bot Name eingeben
3. **Bot** → **Add Bot**
4. **Token** kopieren → in `.env` einfügen
5. **OAuth2** → **URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Administrator` (oder spezifische Rechte)
6. Bot zum Server hinzufügen


## Commands

| Command | Beschreibung |
|---------|--------------|
| `!addgeburtstag` | Geburtstag hinzufügen |
| `!checkgeburtstag` | Geburtstage anzeigen |
| `!epic` | Prüft auf neue Epic Games Spiele |
| `!hilfe` | Interaktiver Google-Suchlink mit Vorschau und anklickbar |
| `!internet` | Prüft, ob eine Internetverbindung besteht (DNS-Auflösung google.com) |
| `!internetping` | Ping-Befehl zu einem Host |
| `!kaschibothilfe` | Zeigt alle verfügbaren Befehle an |
| `!neuerwürfel` | Löscht deine gespeicherte Würfelauswahl |
| `!showposted` | Listet alle bereits geposteten YouTube Videos auf |
| `!steamfree` | Prüft auf neue kostenlose Steam Spiele |
| `!würfel` | Würfelt mit dem zuletzt gewählten Würfel (Cooldown 1h) |
| `!youtube` | Prüft auf neue Videos auf deinen Kanal |


