from discord.ext import commands

def setup(bot: commands.Bot):
    @bot.command(name="bothilfe")
    async def bothilfe(ctx: commands.Context):
        """Listet alle verfügbaren Commands auf."""
        # Alle Command-Namen sammeln, except hidden/system commands
        cmds = sorted(
            cmd.name
            for cmd in bot.commands
            if not cmd.hidden and cmd.enabled
        )
        # Formatieren als !command
        cmd_list = ", ".join(f"!{name}" for name in cmds)
        await ctx.send(f"Hier sind alle Commands:\n{cmd_list}")
