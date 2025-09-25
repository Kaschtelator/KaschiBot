import logging
import sys
import os
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import discord
from discord.ext import commands

import config

# --- Logging einrichten und doppelte Handler entfernen ---
root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)-15s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

logging.getLogger("discord").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("🚀 Kaschibot wird gestartet...")

# --- Bot-Setup ---
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)
MODULE_DIR = os.path.join(os.path.dirname(__file__), "modules")

# Tracket für jedes Modul, welche Commands es registriert hat
loaded_commands = {}

def load_module(name: str):
    logger.info(f"📦 Lade Modul: {name}")
    full = f"modules.{name}"
    try:
        module = importlib.import_module(full)
        before = {c.name for c in bot.commands}
        if hasattr(module, "setup"):
            module.setup(bot)
            logger.debug(f"Setup-Funktion für {name} ausgeführt")
        else:
            logger.warning(f"Modul {name} hat keine setup()-Funktion")
        after = {c.name for c in bot.commands}
        new_cmds = list(after - before)
        loaded_commands[name] = new_cmds
        logger.info(f"✅ Modul geladen: {name} → Commands: {new_cmds}")
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden von Modul {name}: {e}")

def reload_module(name: str):
    logger.info(f"🔄 Lade Modul neu: {name}")

    # Entferne alte Commands, falls registriert
    old_commands = loaded_commands.get(name, [])
    for cmd_name in old_commands:
        if bot.get_command(cmd_name):
            bot.remove_command(cmd_name)
            logger.debug(f"Command '{cmd_name}' entfernt")

    try:
        full = f"modules.{name}"
        module = sys.modules.get(full)
        if module:
            importlib.reload(module)
            logger.debug(f"Modul {name} neu geladen")
        else:
            module = importlib.import_module(full)
            logger.debug(f"Modul {name} importiert")
        before = {c.name for c in bot.commands}
        if hasattr(module, "setup"):
            module.setup(bot)
        after = {c.name for c in bot.commands}
        loaded_commands[name] = list(after - before)
        logger.info(f"🔄 Modul neu geladen: {name} → Commands: {loaded_commands[name]}")
    except Exception as e:
        logger.error(f"❌ Fehler beim Neuladen {name}: {e}")

class ModuleWatcher(FileSystemEventHandler):
    def __init__(self):
        self._debounce = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        name = os.path.splitext(os.path.basename(event.src_path))[0]
        if name == "__init__" or name not in loaded_commands:
            logger.debug(f"Datei {name} ignoriert (nicht überwacht)")
            return

        import time
        now = time.time()
        last = self._debounce.get(name, 0)
        if now - last < 1:  # 1 Sekunde Debounce
            return
        self._debounce[name] = now

        logger.info(f"📝 Dateiänderung erkannt: {name}.py")
        reload_module(name)

@bot.event
async def on_ready():
    logger.info(f"🤖 {bot.user} ist online!")

    try:
        await bot.change_presence(activity=discord.Streaming(
            name=config.STATUS_NAME,
            url=config.STATUS_URL
        ))
        logger.info(f"📺 Status gesetzt: {config.STATUS_NAME}")
    except Exception as e:
        logger.error(f"❌ Fehler beim Setzen des Status: {e}")

    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)
    logger.info(f"🏰 Verbunden mit {guild_count} Server(n) und {member_count} Mitgliedern")

    logger.info(f"👀 Überwache Modul-Verzeichnis: {MODULE_DIR}/")

@bot.event
async def on_guild_join(guild):
    logger.info(f"➕ Neuem Server beigetreten: {guild.name} ({guild.id}) - {guild.member_count} Mitglieder")

@bot.event
async def on_guild_remove(guild):
    logger.info(f"➖ Server verlassen: {guild.name} ({guild.id})")

@bot.event
async def on_command(ctx):
    logger.info(f"🎯 Command '{ctx.command}' ausgeführt von {ctx.author} in #{ctx.channel}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Unbekannter Befehl. Tippe `!bothilfe` für alle verfügbaren Commands.")
    else:
        logger.error(f"❌ Command-Fehler in '{ctx.command}': {error}")

# --- Initiales Laden aller Module ---
logger.info(f"📁 Suche nach Modulen in: {MODULE_DIR}")
module_files = [f for f in os.listdir(MODULE_DIR) if f.endswith(".py") and f != "__init__.py"]
logger.info(f"🔍 {len(module_files)} Module gefunden: {', '.join(module_files)}")

for file in module_files:
    mod = file[:-3]
    load_module(mod)

# --- Watchdog-Observer starten ---
logger.info("👁️ Starte Datei-Watcher für Hot-Reload...")
observer = Observer()
observer.schedule(ModuleWatcher(), path=MODULE_DIR, recursive=False)
observer.start()
logger.info("✅ Hot-Reload Watcher gestartet")

# --- Bot starten ---
logger.info("🔌 Verbinde mit Discord...")
try:
    bot.run(config.TOKEN)
except Exception as e:
    logger.error(f"💥 Bot-Start fehlgeschlagen: {e}")
finally:
    observer.stop()
    observer.join()
    logger.info("👋 Kaschibot wurde beendet")
