import discord

from discord.ext import commands
from discord.embeds import Embed


class Utils(commands.Cog):
    """utilities Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """test bot latency"""
        await ctx.send(embed=Embed(
            title="pong",
            description=f"{self.bot.latency*1000:.0f}ms",
            color=discord.Color.dark_grey(),
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
