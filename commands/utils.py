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
        """Test bot latency"""
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

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Create instant invite"""
        if not isinstance(ctx.channel, discord.abc.GuildChannel):
            raise IntentionalError(
                "Command is only supported on guild server.")
        link = await ctx.channel.create_invite(max_uses=0, max_age=60 * 60)

        await ctx.send(f"{link}", embed=Embed(title="obs.:", description="this invitation is only valid for 1 hour", color=discord.Color.yellow()))

async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
