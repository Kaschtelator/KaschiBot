import aiohttp
import discord
import json
import os
import logging
from discord.ext import tasks, commands
import config
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)
LASTGAME_PATH = "datenbank/lastEpicGames.json"
lastgames = []

# DEBUG-SCHALTER
DEBUG = True

async def read_last_games():
    global lastgames
    if not os.path.exists(LASTGAME_PATH):
        with open(LASTGAME_PATH, "w") as f:
            json.dump([], f, indent=2)
        lastgames = []
        logger.info("Epic Games Datenbank erstellt")
        return

    try:
        with open(LASTGAME_PATH, "r", encoding="utf-8") as f:
            lastgames = json.load(f)
        logger.info(f"Epic Games Datenbank geladen: {len(lastgames)} Einträge")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Epic Games Datenbank: {e}")
        lastgames = []

async def save_last_games():
    global lastgames
    try:
        with open(LASTGAME_PATH, "w", encoding="utf-8") as f:
            json.dump(lastgames, f, indent=2, ensure_ascii=False)
        logger.info("Epic Games Datenbank gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Epic Games Datenbank: {e}")

def debug_log(message: str):
    """Hilfsfunktion für Debug-Logging"""
    if DEBUG:
        logger.debug(f"[DEBUG] {message}")

async def check_epic(bot, status_channel, force_chat_output=False, triggered_by="Unbekannt"):
    global lastgames
    
    if DEBUG:
        logger.info(f"=== EPIC CHECK GESTARTET (Ausgelöst von: {triggered_by}) ===")
    
    await read_last_games()

    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=de-DE&country=DE&allowCountries=DE"
    
    try:
        debug_log(f"Starte HTTP-Request zu: {url}")
        
        async with aiohttp.ClientSession() as session:
            debug_log("ClientSession erstellt")
            
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    logger.info(f"HTTP-Response erhalten: Status {resp.status}")
                    
                    if resp.status != 200:
                        logger.error(f"Epic API Error: {resp.status} (Ausgelöst von: {triggered_by})")
                        if force_chat_output:
                            await status_channel.send("🚫 Fehler beim Abrufen der Epic Games-Daten.")
                        return
                    
                    debug_log("Response-Status ist 200, versuche JSON zu parsen...")
                    
                    try:
                        data = await resp.json()
                        debug_log(f"JSON erfolgreich geparst. Root-Type: {type(data)}")
                        
                        if isinstance(data, dict):
                            debug_log(f"Root ist ein Dictionary. Top-Level Keys: {list(data.keys())}")
                        else:
                            logger.error(f"Root ist KEIN Dictionary, sondern: {type(data)}")
                            return
                        
                        # DEBUG: Speichere die komplette API-Antwort
                        if DEBUG:
                            debug_path = "datenbank/epic_api_debug.json"
                            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                            try:
                                with open(debug_path, "w", encoding="utf-8") as debug_file:
                                    json.dump(data, debug_file, indent=2, ensure_ascii=False)
                                debug_log(f"Debug-Datei gespeichert: {debug_path}")
                            except Exception as save_error:
                                logger.error(f"Fehler beim Speichern der Debug-Datei: {save_error}", exc_info=True)
                        
                    except json.JSONDecodeError as json_error:
                        logger.error(f"JSON Parse-Fehler: {json_error}", exc_info=True)
                        response_text = await resp.text()
                        logger.error(f"Response Text (erste 500 Zeichen): {response_text[:500]}")
                        return
                    except Exception as parse_error:
                        logger.error(f"Unerwarteter Fehler beim JSON-Parsen: {parse_error}", exc_info=True)
                        return
                    
            except asyncio.TimeoutError:
                logger.error("HTTP-Request Timeout (30 Sekunden überschritten)")
                if force_chat_output:
                    await status_channel.send("🚫 Timeout beim Abrufen der Epic Games-Daten.")
                return
            except Exception as http_error:
                logger.error(f"HTTP-Request Fehler: {http_error}", exc_info=True)
                if force_chat_output:
                    await status_channel.send(f"🚫 Fehler beim HTTP-Request: {http_error}")
                return
        
        debug_log("ClientSession geschlossen")
        debug_log("Beginne Datenverarbeitung...")
        
        # Schritt-für-Schritt Zugriff
        debug_log("Schritt 1: Zugriff auf data['data']")
        if "data" not in data:
            logger.error(f"'data' Key existiert nicht. Verfügbare Keys: {list(data.keys())}")
            return
        
        data_root = data.get("data")
        debug_log(f"data['data'] erhalten. Type: {type(data_root)}")
        
        if data_root is None:
            logger.error("data['data'] ist None")
            return
        
        if not isinstance(data_root, dict):
            logger.error(f"data['data'] ist kein Dictionary: {type(data_root)}")
            return
        
        debug_log(f"data['data'] ist Dictionary. Keys: {list(data_root.keys())}")
        
        # Schritt 2
        debug_log("Schritt 2: Zugriff auf data['data']['Catalog']")
        if "Catalog" not in data_root:
            logger.error(f"'Catalog' Key existiert nicht. Verfügbare Keys: {list(data_root.keys())}")
            return
        
        catalog = data_root.get("Catalog")
        debug_log(f"Catalog erhalten. Type: {type(catalog)}")
        
        if catalog is None:
            logger.error("Catalog ist None")
            return
        
        if not isinstance(catalog, dict):
            logger.error(f"Catalog ist kein Dictionary: {type(catalog)}")
            return
        
        debug_log(f"Catalog ist Dictionary. Keys: {list(catalog.keys())}")
        
        # Schritt 3
        debug_log("Schritt 3: Zugriff auf searchStore")
        if "searchStore" not in catalog:
            logger.error(f"'searchStore' Key existiert nicht. Verfügbare Keys: {list(catalog.keys())}")
            return
        
        searchStore = catalog.get("searchStore")
        debug_log(f"searchStore erhalten. Type: {type(searchStore)}")
        
        if searchStore is None:
            logger.error("searchStore ist None")
            return
        
        if not isinstance(searchStore, dict):
            logger.error(f"searchStore ist kein Dictionary: {type(searchStore)}")
            return
        
        debug_log(f"searchStore ist Dictionary. Keys: {list(searchStore.keys())}")
        
        # Schritt 4
        debug_log("Schritt 4: Zugriff auf elements")
        if "elements" not in searchStore:
            logger.error(f"'elements' Key existiert nicht. Verfügbare Keys: {list(searchStore.keys())}")
            return
        
        promotions = searchStore.get("elements")
        debug_log(f"elements erhalten. Type: {type(promotions)}")
        
        if promotions is None:
            logger.error("elements ist None")
            promotions = []
        
        if not isinstance(promotions, list):
            logger.error(f"elements ist keine Liste: {type(promotions)}")
            promotions = []
        
        logger.info(f"elements ist Liste mit {len(promotions)} Elementen")

        if not promotions:
            logger.info(f"Keine Epic Games Promotions gefunden (Ausgelöst von: {triggered_by})")
            if force_chat_output:
                await status_channel.send("ℹ️ Zurzeit sind keine Gratis-Spiele im Epic Games Store verfügbar.")
            return

        logger.info(f"Beginne Verarbeitung von {len(promotions)} Spielen...")

        # Hole den Freegames-Channel - WICHTIG für alle Postings
        freegames_channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
        if not freegames_channel:
            logger.error(f"Freegames-Channel {config.FREEGAMES_DISCORD_CHANNEL_ID} nicht gefunden!")
            if force_chat_output:
                await status_channel.send("⚠️ Freegames-Channel nicht gefunden!")
            return

        new_games_count = 0
        for idx, game in enumerate(promotions):
            try:
                debug_log(f"Verarbeite Spiel #{idx}")
                
                if not isinstance(game, dict):
                    debug_log(f"Spiel #{idx} ist kein Dictionary: {type(game)}")
                    continue

                title = game.get("title", "Unbekannt")
                game_id = game.get("id")
                
                # Prüfe die Promotions-Struktur
                promotions_obj = game.get("promotions")
                debug_log(f"Spiel #{idx} ({title}): promotions_obj = {type(promotions_obj)}")
                
                if not promotions_obj or not isinstance(promotions_obj, dict):
                    debug_log(f"Spiel #{idx} ({title}): Keine gültigen promotions")
                    continue
                
                promotional_offers = promotions_obj.get("promotionalOffers")
                debug_log(f"Spiel #{idx} ({title}): promotionalOffers vorhanden = {promotional_offers is not None and len(promotional_offers) > 0}")
                
                if not promotional_offers or len(promotional_offers) == 0:
                    debug_log(f"Spiel #{idx} ({title}): Keine promotionalOffers gefunden")
                    continue
                
                # **WICHTIG:** Prüfe ob es wirklich KOSTENLOS (100% Rabatt) ist!
                is_free_game = False
                discount_percentage = None
                end_date = None
                
                for offer_idx, offer in enumerate(promotional_offers):
                    if isinstance(offer, dict):
                        promo_data = offer.get("promotionalOffers", [])
                        if promo_data and len(promo_data) > 0:
                            for promo in promo_data:
                                if isinstance(promo, dict):
                                    discount_setting = promo.get("discountSetting", {})
                                    if isinstance(discount_setting, dict):
                                        discount_pct = discount_setting.get("discountPercentage", 0)
                                        discount_percentage = discount_pct
                                        
                                        # Ende-Datum der Promotion
                                        end_date = promo.get("endDate", "Unbekannt")
                                        
                                        # NUR 100% Rabatt = Kostenlos!
                                        if discount_pct == 0 or discount_pct == 100:
                                            is_free_game = True
                                            debug_log(f"Spiel #{idx} ({title}): ✓ Kostenlos erkannt! (Rabatt: {discount_pct}%)")
                                            break
                                        else:
                                            debug_log(f"Spiel #{idx} ({title}): Nur {discount_pct}% Rabatt (nicht kostenlos)")
                    
                    if is_free_game:
                        break
                
                if not is_free_game:
                    debug_log(f"Spiel #{idx} ({title}): Nicht kostenlos (Rabatt: {discount_percentage}%)")
                    continue

                # Prüfe ob bereits gepostet
                if not game_id:
                    logger.warning(f"Spiel #{idx} ({title}): Keine ID")
                    continue
                    
                if any(g.get("id") == game_id for g in lastgames):
                    debug_log(f"Spiel #{idx} ({title}): Bereits gepostet")
                    continue
                
                logger.info(f"✓ Neues kostenloses Spiel gefunden: {title}")
                
                # Bundle-/Produkt-URL-Ermittlung
                catalogNs = game.get("catalogNs")
                offerMappings = game.get("offerMappings", [])
                pageSlug = ""
                pageType = ""
                namespace = ""
                
                # 1. Priorität: offerMappings
                if offerMappings and isinstance(offerMappings, list) and len(offerMappings) > 0:
                    first_mapping = offerMappings[0]
                    if isinstance(first_mapping, dict):
                        pageSlug = first_mapping.get("pageSlug", "") or pageSlug
                        pageType = first_mapping.get("pageType", "") or pageType
                
                # 2. Priorität: catalogNs.mappings
                if (not pageSlug) and catalogNs and isinstance(catalogNs, dict):
                    namespace = catalogNs.get("namespace", "") or namespace
                    mappings = catalogNs.get("mappings")
                    if mappings and isinstance(mappings, list) and len(mappings) > 0:
                        first_mapping = mappings[0]
                        if isinstance(first_mapping, dict):
                            pageSlug = first_mapping.get("pageSlug", "") or pageSlug
                            pageType = first_mapping.get("pageType", "") or pageType
                
                # 3. Fallback: productSlug
                if not pageSlug:
                    pageSlug = game.get("productSlug", "") or ""
                
                # Kategorien auswerten
                categories = game.get("categories", [])
                category_paths = [
                    c.get("path") for c in categories
                    if isinstance(c, dict) and isinstance(c.get("path"), str)
                ]
                
                # Robust: Bundle-Erkennung
                is_bundle = (
                    (isinstance(pageType, str) and pageType.lower() == "bundle") or
                    namespace == "bundles" or
                    any(p == "bundles" or p.startswith("bundles/") for p in category_paths) or
                    ("bundle" in pageSlug.lower() if isinstance(pageSlug, str) else False)
                )
                
                debug_log(
                    f"Spiel #{idx} ({title}): pageType='{pageType}', "
                    f"namespace='{namespace}', pageSlug='{pageSlug}', "
                    f"categories={category_paths}, is_bundle={is_bundle}"
                )
                
                if pageSlug:
                    if is_bundle:
                        game_url = f"https://www.epicgames.com/store/de/bundles/{pageSlug}"
                    else:
                        game_url = f"https://www.epicgames.com/store/de/p/{pageSlug}"
                else:
                    game_url = "https://www.epicgames.com/store/de/"
                
                debug_log(f"Spiel #{idx} ({title}): Final URL: {game_url}")
                
                keyImages = game.get("keyImages", [])
                game_image = "https://cdn2.unrealengine.com/placeholder-image.jpg"
                if keyImages and isinstance(keyImages, list) and len(keyImages) > 0:
                    first_image = keyImages[0]
                    if isinstance(first_image, dict):
                        game_image = first_image.get("url", game_image)
                
                original_price_raw = ""
                price_obj = game.get("price")
                if price_obj and isinstance(price_obj, dict):
                    totalPrice = price_obj.get("totalPrice")
                    if totalPrice and isinstance(totalPrice, dict):
                        fmtPrice = totalPrice.get("fmtPrice")
                        if fmtPrice and isinstance(fmtPrice, dict):
                            original_price_raw = fmtPrice.get("originalPrice", "")
                
                if original_price_raw and original_price_raw not in ["€0.00", "0", "0 €", "0,00 €"]:
                    original_price = f"💰 {original_price_raw} **→ Kostenlos!**"
                else:
                    original_price = "💰 **Kostenlos!**"
                
                embed = discord.Embed(
                    title=f"Kostenlos bei Epic Games: {title}",
                    description=f"Schnapp es dir 👉 [Epicgames.com]({game_url}) 👈",
                    color=0xffb700
                )
                embed.set_image(url=game_image)
                embed.add_field(name="Originalpreis", value=original_price)
                
                # IMMER im Freegames-Channel posten
                await freegames_channel.send("@everyone", embed=embed)
                logger.info(f"✓ Spiel gepostet in #{freegames_channel.name}: {title}")

                # Speichere vollständige Informationen
                lastgames.append({
                    "id": game_id,
                    "title": title,
                    "url": game_url,
                    "image": game_image,
                    "original_price": original_price_raw,
                    "posted_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": end_date,
                    "discount": discount_percentage
                })
                new_games_count += 1
                logger.info(f"✓ Spiel erkannt und gepostet: {title}")

            except Exception as e:
                logger.error(f"Fehler bei Spiel #{idx}: {e}", exc_info=True)
                continue

        await save_last_games()
        
        if new_games_count == 0:
            logger.info(f"Keine neuen Epic Games gefunden (Ausgelöst von: {triggered_by})")
            if force_chat_output:
                await status_channel.send("✔️ Keine neuen kostenlosen Spiele entdeckt.")
        else:
            logger.info(f"Epic Games Check abgeschlossen: {new_games_count} neue Spiele gefunden")
            if force_chat_output:
                await status_channel.send(
                    f"✅ {new_games_count} neue kostenlose Spiele wurden im Freegames-Channel gepostet!"
                )
        
        if DEBUG:
            logger.info(f"=== EPIC CHECK BEENDET ===\n")

    except Exception as e:
        logger.error(f"KRITISCHER FEHLER: {e} (Ausgelöst von: {triggered_by})", exc_info=True)
        if force_chat_output:
            await status_channel.send(f"⛔ Fehler beim Epic Games-Check: {e}")

def setup(bot):
    asyncio.run(read_last_games())

    @tasks.loop(minutes=30)
    async def epic_check():
        logger.info("Starte automatischen Epic Games Check (Task)")
        channel = bot.get_channel(config.FREEGAMES_DISCORD_CHANNEL_ID)
        if channel:
            await check_epic(bot, channel, force_chat_output=False, triggered_by="Auto-Task")
        else:
            logger.error("Epic Games Channel nicht gefunden (Task)")

    @bot.command()
    async def epic(ctx):
        """Prüft auf neue Epic Games Spiele"""
        logger.info(f"Manueller Epic Games Check durch {ctx.author}")
        
        await ctx.send("🔎 Suche nach neuen kostenlosen Spielen im Epic Games Store ...")
        
        # Status-Messages gehen an den Befehl-Sender (DM oder Channel)
        # Spiele gehen IMMER im Freegames-Channel
        await check_epic(bot, ctx, force_chat_output=True, triggered_by=str(ctx.author))

    @bot.listen()
    async def on_ready():
        if not epic_check.is_running():
            epic_check.start()
            logger.info("Epic Games Check Task gestartet (alle 30 Minuten)")
