import dns.resolver
import asyncio
from subprocess import PIPE
from discord.ext import commands

def setup(bot):
    @bot.command()
    async def internet(ctx):
        """Prüft, ob eine Internetverbindung besteht (DNS-Auflösung google.com)."""
        try:
            answers = dns.resolver.resolve('google.com', 'A')
            if answers:
                await ctx.send("Ich bin mit dem Internet verbunden.")
            else:
                await ctx.send("Keine Internetverbindung erkannt.")
        except Exception:
            await ctx.send("Keine Internetverbindung erkannt.")

    @bot.command()
    async def internetping(ctx, host: str = None):
        """Ping-Befehl: !internetping <host>"""
        if not host:
            await ctx.send("Bitte gib eine Adresse zum Pingen an, z.B. `!internetping google.com`")
            return
        
        # Entferne evtl. http/https
        host = host.replace('http://', '').replace('https://', '')

        await ctx.send(f"Starte Ping zu {host}… bitte warten.")

        # DNS-Auflösung
        try:
            answers = dns.resolver.resolve(host, 'A')
            ip = answers[0].to_text()
        except Exception as e:
            await ctx.send(f"DNS-Auflösung für {host} fehlgeschlagen: {e}")
            return
        
        # Ping ausführen (Linux ping -c 5)
        try:
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '5', ip,
                stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = await process.communicate()
            result = stdout.decode() if stdout else stderr.decode()
            
            # Ausgabe kürzen falls zu lang
            if len(result) > 1900:
                result = result[:1900] + "\n... Ausgabe gekürzt ..."
            
            await ctx.send(f"Ping-Ergebnis zu {host} ({ip}):\n``````")
        except Exception as e:
            await ctx.send(f"Fehler beim Ping: {e}")
