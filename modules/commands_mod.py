from discord.ext import commands
import discord

def split_text(text, max_length=1024):
    """Teilt einen langen Text in mehrere Strings auf, die maximal max_length lang sind."""
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def setup(bot: commands.Bot):

    @bot.command(name="bothilfe")
    async def bothilfe(ctx: commands.Context):
        """Zeigt alle verfügbaren Commands in einem Embed an."""

        embed = discord.Embed(title="Befehlsübersicht", color=0x00ff00)
        cogs = {}

        for cmd in bot.commands:
            if cmd.hidden or not cmd.enabled:
                continue
            cog_name = cmd.cog_name if cmd.cog_name else "Keine Kategorie"
            if cog_name not in cogs:
                cogs[cog_name] = []
            cogs[cog_name].append(cmd)

        for cog_name in sorted(cogs):
            cmds = cogs[cog_name]
            cmds.sort(key=lambda c: c.name)
            field_value = ""
            for cmd in cmds:
                description = cmd.help or "Keine Beschreibung"
                field_value += f"**!{cmd.name}** - {description}\n"
            
            # Text aufteilen wenn länger als 1024
            chunks = split_text(field_value)
            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"{cog_name}" if i == 0 else f"{cog_name} (Fortsetzung)",
                    value=chunk,
                    inline=False
                )

        await ctx.send(embed=embed)
