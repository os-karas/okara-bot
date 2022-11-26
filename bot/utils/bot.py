import os

from discord.ext import commands


async def load_module_extensions(bot: commands.Bot, dir: str):
    for file in os.listdir(dir):
        if not file.endswith(".py"):
            continue
        module = dir.replace("/", ".")

        await bot.load_extension(f"{module}.{file[:-3]}")
