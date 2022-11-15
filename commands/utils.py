import discord

from discord.ext import commands
from discord.embeds import Embed

from errors.events import IntentionalError


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

    @commands.command(name="calc", aliases=["calculate", "calculator"])
    async def calculate(self, ctx: commands.Context, *, calc: str):
        """calculate math expressions"""

        if calc.__len__() > 50:
            raise IntentionalError("The accepted character limit is 50.")

        await ctx.send(embed=Embed(
            title=calc,
            description=eval(calc),
            color=discord.Color.dark_green()
        ))

    @calculate.error
    async def calculate_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, commands.CommandInvokeError):
            ctx.command_failed = False
            return await ctx.message.reply("Invalid calculation, enter a valid calculation.")
        if isinstance(err, commands.MissingRequiredArgument):
            ctx.command_failed = False
            return await ctx.message.reply("the calculation is a required argument.",)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
