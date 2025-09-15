import discord
from discord.ext import commands
import urllib.parse
import asyncio

def setup(bot: commands.Bot):
    @bot.command(name="hilfe")
    async def hilfe(ctx: commands.Context):
        """Interaktiver Google-Suchlink mit Vorschau und anklickbar."""
        await ctx.send("Was möchtest du googeln? Bitte gib deine Suchanfrage ein.")

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Zeit abgelaufen. Probiere es später noch einmal mit `!hilfe`.")
            return

        query = msg.content.strip()
        if not query:
            await ctx.send("Leere Suche. Bitte versuche es erneut mit `!hilfe`.")
            return

        # URL richtig escapen
        escaped = urllib.parse.quote_plus(query)
        google_url = f"https://www.google.com/search?q={escaped}"

        # Sende den Link *allein* in einer Nachricht, damit Discord automatisch eine Vorschau lädt.
        await ctx.send(f"Hier dein Suchlink für **{query}**:\n{google_url}")
