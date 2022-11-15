import os

from discord.ext import commands


async def load_module_extensions(bot: commands.Bot, module: str):
    for file in os.listdir(module):
        if not file.endswith(".py"):
            continue
        await bot.load_extension(f"{module}.{file[:-3]}")