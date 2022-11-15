from discord.ext.commands import errors
from discord.ext import commands


class Errors(commands.Cog):
    """toogle status"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        return await ctx.message.reply(str(error))


async def setup(bot: commands.Bot):
    await bot.add_cog(Errors(bot))
