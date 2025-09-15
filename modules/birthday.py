import discord
import json
import os
import logging
from discord.ext import tasks, commands
from datetime import datetime, timedelta, time
import config

logger = logging.getLogger(__name__)
BDAY_PATH = "datenbank/birthdays.json"

def setup(bot):
    if not os.path.exists(BDAY_PATH):
        with open(BDAY_PATH, "w") as f:
            json.dump([], f)
        logger.info("Geburtstags-Datenbank erstellt")

    @bot.command()
    async def addgeburtstag(ctx, name: str = None, date: str = None):
        """!addgeburtstag Name TT-MM"""
        
        # Prüfe ob Parameter fehlen
        if name is None or date is None:
            embed = discord.Embed(
                title="❌ Fehlende Parameter",
                description="Du musst Name und Datum angeben!",
                color=0xff0000
            )
            embed.add_field(
                name="Verwendung:", 
                value="`!addgeburtstag Name TT-MM`",
                inline=False
            )
            embed.add_field(
                name="Beispiel:", 
                value="`!addgeburtstag Max 15-03`",
                inline=False
            )
            await ctx.send(embed=embed)
            logger.info(f"Geburtstag-Command falsch verwendet von {ctx.author}")
            return

        try:
            datetime.strptime(date, "%d-%m")
        except ValueError:
            embed = discord.Embed(
                title="❌ Ungültiges Datum",
                description="Das Datum muss im Format **TT-MM** sein!",
                color=0xff0000
            )
            embed.add_field(
                name="Beispiele:", 
                value="15-03 (für 15. März)\n07-12 (für 7. Dezember)",
                inline=False
            )
            await ctx.send(embed=embed)
            logger.warning(f"Ungültiges Datum '{date}' von {ctx.author}")
            return

        jahr = datetime.utcnow().year - 1

        with open(BDAY_PATH, "r") as f:
            birthdays = json.load(f)

        # Prüfe ob Name bereits existiert
        for existing in birthdays:
            if existing["name"].lower() == name.lower():
                embed = discord.Embed(
                    title="⚠️ Name bereits vorhanden",
                    description=f"Ein Geburtstag für **{existing['name']}** ist bereits am **{existing['date']}** eingetragen.",
                    color=0xffa500
                )
                await ctx.send(embed=embed)
                logger.info(f"Geburtstag für {name} bereits vorhanden")
                return

        birthdays.append({"name": name, "date": date, "jahr": jahr})

        with open(BDAY_PATH, "w") as f:
            json.dump(birthdays, f)

        embed = discord.Embed(
            title="✅ Geburtstag hinzugefügt",
            description=f"Geburtstag von **{name}** am **{date}** wurde erfolgreich hinzugefügt!",
            color=0x00ff00
        )
        embed.add_field(name="🎂", value="Dankeschön!", inline=False)
        await ctx.send(embed=embed)
        logger.info(f"Geburtstag hinzugefügt: {name} am {date}")

    @bot.command()
    async def checkgeburtstag(ctx):
        """Zeigt Geburtstage heute (wenn vorhanden) und die nächsten kommenden Geburtstage an."""
        heute = datetime.utcnow()
        logger.info(f"Geburtstags-Check angefordert von {ctx.author}")

        with open(BDAY_PATH, "r") as f:
            birthdays = json.load(f)

        if not birthdays:
            embed = discord.Embed(
                title="📅 Keine Geburtstage",
                description="Es sind noch keine Geburtstage eingetragen.",
                color=0x808080
            )
            embed.add_field(
                name="Geburtstag hinzufügen:",
                value="`!addgeburtstag Name TT-MM`",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        # Filter Geburtstage heute
        heute_tagmon = (heute.day, heute.month)
        geburtstage_heute = [g for g in birthdays if tuple(map(int, g["date"].split("-"))) == heute_tagmon]

        # Nächsten Geburtstag ermitteln
        def next_birthday_date(g):
            tag, monat = map(int, g["date"].split("-"))
            jahr = heute.year
            geb_datum = datetime(jahr, monat, tag)
            if geb_datum < heute:
                geb_datum = datetime(jahr + 1, monat, tag)  # nächstes Jahr
            return geb_datum

        birthdays_sorted = sorted(birthdays, key=next_birthday_date)

        embed = discord.Embed(
            title="🎉 Geburtstags-Übersicht",
            color=0xff69b4
        )

        if geburtstage_heute:
            names = ', '.join(g['name'] for g in geburtstage_heute)
            embed.add_field(
                name="🎂 Heute haben Geburtstag:",
                value=f"**{names}**",
                inline=False
            )
            logger.info(f"Geburtstage heute: {names}")
        else:
            embed.add_field(
                name="📅 Heute:",
                value="Niemand hat heute Geburtstag",
                inline=False
            )

        if birthdays_sorted:
            next_birthday = birthdays_sorted[0]
            next_birthday_date_obj = next_birthday_date(next_birthday)
            diff = (next_birthday_date_obj - heute).days
            
            if diff == 0 and not geburtstage_heute:
                # Falls heute Geburtstag ist, aber nicht in geburtstage_heute (Edge Case)
                embed.add_field(
                    name="🎈 Nächster Geburtstag:",
                    value=f"**{next_birthday['name']}** - heute!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎈 Nächster Geburtstag:",
                    value=f"**{next_birthday['name']}** am **{next_birthday['date']}** (in {diff} Tagen)",
                    inline=False
                )

        await ctx.send(embed=embed)

    @tasks.loop(time=time(hour=9, minute=0))  # Täglich um 9:00 Uhr
    async def daily_birthday_check():
        """Automatische tägliche Geburtstagsprüfung um 9:00 Uhr"""
        logger.info("Starte täglichen Geburtstags-Check (9:00 Uhr)")
        channel = bot.get_channel(config.BDAY_DISCORD_CHANNEL_ID)
        if not channel:
            logger.error("Geburtstags-Channel nicht gefunden")
            return

        heute = datetime.utcnow()

        try:
            with open(BDAY_PATH, "r") as f:
                birthdays = json.load(f)

            # Filter Geburtstage heute
            heute_tagmon = (heute.day, heute.month)
            geburtstage_heute = [g for g in birthdays if tuple(map(int, g["date"].split("-"))) == heute_tagmon]

            if geburtstage_heute:
                names = ', '.join(g['name'] for g in geburtstage_heute)
                embed = discord.Embed(
                    title="🎉 Herzlichen Glückwunsch! 🎉",
                    description=f"Heute haben Geburtstag: **{names}**",
                    color=0xff69b4
                )
                embed.add_field(name="🎂", value="Alles Gute zum Geburtstag!", inline=False)
                
                await channel.send("@everyone", embed=embed)
                logger.info(f"Geburtstags-Nachricht gepostet für: {names}")
            else:
                logger.info("Keine Geburtstage heute")

        except Exception as e:
            logger.error(f"Fehler beim Geburtstags-Check: {e}")

    @bot.listen()
    async def on_ready():
        if not daily_birthday_check.is_running():
            daily_birthday_check.start()
            logger.info("Täglicher Geburtstags-Check gestartet (täglich um 9:00 Uhr)")
