#!/usr/bin/env python

"""A simple bot from discord"""

__author__ = "Kauan Augusto"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Rob Knight"
__email__ = "kauaug.mo@gmail.com"
__status__ = "Development"

import asyncio
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

from bot.commands.help import HelpCommand
from bot.utils.bot import load_module_extensions


async def load_extensions(bot: commands.Bot):
    await load_module_extensions(bot, "bot/cogs/commands")
    await load_module_extensions(bot, "bot/cogs/tasks")
    await load_module_extensions(bot, "bot/cogs/events")


load_dotenv()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("_"),
    intents=discord.Intents.all(),
    help_command=HelpCommand())


@bot.command()
async def hello(ctx):
    """world"""
    await ctx.send("world")


asyncio.run(load_extensions(bot))
bot.run(os.getenv("BOT_TOKEN") or "")
