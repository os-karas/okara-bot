#!/usr/bin/env python

"""A simple bot from discord"""

__author__ = "Kauan Augusto"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = []
__license__ = "MIT"
__version__ = "0.2.0"
__maintainer__ = "Rob Knight"
__email__ = "kauaug.mo@gmail.com"
__status__ = "Development"

import asyncio
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from utils.bot import load_module_extensions


async def load_extensions(bot: commands.Bot):
    await load_module_extensions(bot, "commands")
    await load_module_extensions(bot, "tasks")
    await load_module_extensions(bot, "events")


load_dotenv()

bot = commands.Bot(command_prefix="_", intents=discord.Intents.all())


@bot.command()
async def hello(ctx):
    """world"""
    await ctx.send("world")


asyncio.run(load_extensions(bot))
bot.run(os.getenv("BOT_TOKEN") or "")
