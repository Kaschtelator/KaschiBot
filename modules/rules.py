import discord
from discord.ext import commands
import json
import os
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)
RULES_PATH = "datenbank/rules_accepted.json"

RULES_CHANNEL_ID = config.RULES_CHANNEL_ID
NEW_USER_ROLE_NAME = "Unbekannter Neuling"
VERIFIED_ROLE_NAME = "Recke"
CONFIRMATION_TEXT = "ich habe verstanden"


async def load_rules_data():
    if not os.path.exists(RULES_PATH):
        os.makedirs(os.path.dirname(RULES_PATH), exist_ok=True)
        with open(RULES_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Rules-Daten: {e}")
        return {}


async def save_rules_data(data):
    try:
        os.makedirs(os.path.dirname(RULES_PATH), exist_ok=True)
        with open(RULES_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Rules-Daten gespeichert")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Rules-Daten: {e}")


def setup(bot: commands.Bot):
    rules_data = {}

    @bot.event
    async def on_ready():
        nonlocal rules_data
        rules_data = await load_rules_data()
        logger.info(f"Rules-Modul geladen (Channel ID: {RULES_CHANNEL_ID})")

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id != RULES_CHANNEL_ID:
            return

        if CONFIRMATION_TEXT.lower() not in message.content.lower():
            return

        nonlocal rules_data
        user = message.author
        guild = message.guild

        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        
        if verified_role is None:
            try:
                await message.reply(f"❌ Fehler: Die Rolle **{VERIFIED_ROLE_NAME}** existiert nicht!")
            except Exception as e:
                logger.error(f"Fehler beim Senden der Fehlermeldung: {e}")
            return

        if verified_role in user.roles:
            try:
                await message.reply(f"⚠️ Du hast bereits die Rolle **{VERIFIED_ROLE_NAME}**!")
            except Exception as e:
                logger.error(f"Fehler beim Senden der Warnung: {e}")
            return

        try:
            await user.add_roles(verified_role)

            new_user_role = discord.utils.get(guild.roles, name=NEW_USER_ROLE_NAME)
            if new_user_role and new_user_role in user.roles:
                try:
                    await user.remove_roles(new_user_role)
                except Exception as e:
                    logger.error(f"Fehler beim Entfernen der Neuling-Rolle: {e}")

            if "accepted_users" not in rules_data:
                rules_data["accepted_users"] = {}

            rules_data["accepted_users"][str(user.id)] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            await save_rules_data(rules_data)

            embed = discord.Embed(
                title="✅ Willkommen!",
                description=f"Hallo {user.mention}! Du hast jetzt die Rolle **{VERIFIED_ROLE_NAME}** und kannst auf alle Kanäle zugreifen.",
                color=0x00ff00
            )
            await message.reply(embed=embed)

            try:
                await message.delete()
                logger.info(f"Nachricht von {user.name} gelöscht")
            except Exception as e:
                logger.error(f"Fehler beim Löschen der Nachricht: {e}")

            logger.info(f"{user.name} hat die Regeln akzeptiert und bekam die Rolle {VERIFIED_ROLE_NAME}")

        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Rolle: {e}")
            try:
                await message.reply("❌ Ein Fehler ist aufgetreten!")
            except:
                pass

    @bot.command(name="rulestatus")
    @commands.has_permissions(administrator=True)
    async def rulestatus(ctx: commands.Context, user: discord.User = None):
        nonlocal rules_data

        if user is None:
            embed = discord.Embed(
                title="❌ Fehlendes Argument",
                description="Du musst einen Nutzer angeben!",
                color=0xff0000
            )
            embed.add_field(name="Verwendung:", value="`!rulestatus @Nutzer`", inline=False)
            await ctx.send(embed=embed)
            return

        user_id = str(user.id)
        if user_id in rules_data.get("accepted_users", {}):
            accepted_at = rules_data["accepted_users"][user_id]
            embed = discord.Embed(
                title="✅ Regeln bestätigt",
                description=f"**{user.mention}** hat die Regeln akzeptiert",
                color=0x00ff00
            )
            embed.add_field(name="Bestätigt am:", value=accepted_at, inline=False)
        else:
            embed = discord.Embed(
                title="❌ Regeln nicht bestätigt",
                description=f"**{user.mention}** hat die Regeln noch nicht akzeptiert",
                color=0xff0000
            )

        await ctx.send(embed=embed)

    @bot.command(name="resetrule")
    @commands.has_permissions(administrator=True)
    async def resetrule(ctx: commands.Context, user: discord.User = None):
        nonlocal rules_data

        if user is None:
            embed = discord.Embed(
                title="❌ Fehlendes Argument",
                description="Du musst einen Nutzer angeben!",
                color=0xff0000
            )
            embed.add_field(name="Verwendung:", value="`!resetrule @Nutzer`", inline=False)
            await ctx.send(embed=embed)
            return

        user_id = str(user.id)
        if user_id in rules_data.get("accepted_users", {}):
            del rules_data["accepted_users"][user_id]
            await save_rules_data(rules_data)

            guild = ctx.guild
            verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
            new_user_role = discord.utils.get(guild.roles, name=NEW_USER_ROLE_NAME)
            
            if verified_role:
                try:
                    await user.remove_roles(verified_role)
                except Exception as e:
                    logger.error(f"Fehler beim Entfernen der Rolle: {e}")

            if new_user_role:
                try:
                    await user.add_roles(new_user_role)
                except Exception as e:
                    logger.error(f"Fehler beim Hinzufügen der Neuling-Rolle: {e}")

            embed = discord.Embed(
                title="✅ Status zurückgesetzt",
                description=f"Regel-Status von **{user.mention}** wurde zurückgesetzt",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"Regel-Status von {user.name} wurde zurückgesetzt")
        else:
            embed = discord.Embed(
                title="⚠️ Nutzer nicht gefunden",
                description=f"**{user.mention}** hat die Regeln noch nicht akzeptiert",
                color=0xffa500
            )
            await ctx.send(embed=embed)
