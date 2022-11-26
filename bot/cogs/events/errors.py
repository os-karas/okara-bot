import discord
import re

from discord.ext import commands


class Errors(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.message.reply("send a `help` command for more information", embed=self.embed_error(error))
        if not ctx.command_failed:
            return

        if isinstance(error, commands.CommandInvokeError):
            raise error.original
        if isinstance(error, commands.CommandError):
            return await ctx.message.reply(embed=self.embed_error(error))

    def embed_error(self, error: commands.CommandError):
        name_class_error = " ".join(
            re.findall('[a-zA-Z][^A-Z]*', error.__class__.__name__)
        )
        return discord.Embed(title=name_class_error,
                             description=f"{error}",
                             color=discord.Color.dark_red())


async def setup(bot: commands.Bot):
    await bot.add_cog(Errors(bot))
