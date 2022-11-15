from discord.ext import commands


class IntentionalError(commands.CommandError):
    """Exception when there is a conflict caused by the bot, which did not consider a user error.

    This inherited from :exc:`CommandError`.
    """

    pass
