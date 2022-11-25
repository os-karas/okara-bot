import discord
import typing

from discord.ext import commands

from commands.musics import checks
from commands.musics.source import YouTubeSource
from contexts.musics import GuildBotVoicedContext, GuildVoicedAllowedContext


class Music(commands.Cog):
    """Music Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        return True

    @commands.command(aliases=["summon", "spawn", "connect"])
    @checks.not_has_voice_client()
    async def join(self,
                   ctx: GuildBotVoicedContext, *,
                   channel: typing.Optional[discord.VoiceChannel] = None):
        """Joins a voice channel."""

        if channel:
            destination = channel
        else:
            if ctx.author.voice is None:
                raise checks.AuthorNotConnected()
            if ctx.author.voice.channel is None:
                raise checks.BotNotPermission()
            destination = ctx.author.voice.channel
        await destination.connect()

        await ctx.send(
            embed=discord.Embed(
                title="joined the channel",
                description=f"The bot joined the {destination.mention} voice channel",
                color=discord.Color.dark_blue()))

    @commands.command(aliases=["disconnect", "exit", "quit"])
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def leave(self, ctx: GuildVoicedAllowedContext):
        """Joins a voice channel."""

        await ctx.voice_client.disconnect(force=True)
        await ctx.send(
            embed=discord.Embed(
                title="left the channel",
                description=f"The bot left the {ctx.author.voice.channel.mention} voice channel",
                color=discord.Color.dark_red()))

    @commands.command(aliases=['vol'])
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def volume(self, ctx: GuildVoicedAllowedContext, *, volume: int):
        """Sets the volume of the player."""
        if not isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            raise checks.BotNotPlaying()
        if 0 > volume or volume > 100:
            raise commands.RangeError(volume, 0, 100)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(
            embed=discord.Embed(
                title="volume updated",
                description=f'Volume of the player set to {volume}%',
                color=discord.Color.dark_teal()))

    @commands.command(aliases=["song", "music"])
    async def play(self, ctx: GuildVoicedAllowedContext, *, search: str):
        """Plays a new song."""
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.author.voice.channel != ctx.voice_client.channel:
            raise checks.VoiceError(
                "You are not connected to the Bot's voice channel.")

        async with ctx.typing():
            source = await YouTubeSource.create_source(ctx, search, loop=self.bot.loop)
            await ctx.send(embed=discord.Embed(
                title=f'enqueued music',
                description=f"The song '{source}' has been queued",
                color=discord.Color.dark_magenta()))
            ctx.voice_client.play(source)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
