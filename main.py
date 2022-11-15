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

import os
import discord

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

bot = commands.Bot(command_prefix="_", intents=discord.Intents.all())


@bot.command()
async def hello(ctx):
    """world"""
    await ctx.send("world")


bot.run(os.getenv("BOT_TOKEN") or "")
