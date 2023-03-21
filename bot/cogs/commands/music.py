import math
import discord
import typing

from discord.ext import commands

from bot.contexts.musics import GuildBotVoicedContext, GuildVoicedAllowedContext
from bot.contexts.all import GuildContext
from bot.commands.musics import checks
from bot.commands.musics.source import YouTubeSource
from bot.commands.musics.state import VoiceState, VoiceStateContext
from bot.commands.musics.song import NoCurrentMusic, Song, QueueEmpty


class Music(commands.Cog):
    """Music Commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.voice_states: dict[int, VoiceState] = {}

    def get_voice_state(self, ctx: GuildContext):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    async def cog_before_invoke(self, ctx: VoiceStateContext):
        ctx.voice_state = self.get_voice_state(ctx)

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                'This command can\'t be used in DM channels.')

        return True

    @commands.command(aliases=["summon", "spawn", "connect"])
    @checks.not_has_voice_client()
    async def join(self,
                   ctx: GuildBotVoicedContext, *,
                   channel: typing.Optional[discord.VoiceChannel] = None):
        """Joins a voice channel"""

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
        """Leave voice channel"""

        await ctx.voice_client.disconnect(force=True)
        await ctx.send(
            embed=discord.Embed(
                title="left the channel",
                description=f"The bot left the {ctx.author.voice.channel.mention} voice channel",
                color=discord.Color.dark_red()))

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(aliases=['vol'])
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def volume(self, ctx: GuildVoicedAllowedContext, *, volume: typing.Optional[int] = None):
        """Sets the volume of the player"""
        if not isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            raise checks.BotNotPlaying()

        if volume is None:
            return await ctx.send(
                embed=discord.Embed(
                    title="volume",
                    description=f'Volume of the player set to {int(ctx.voice_client.source.volume * 100)}%',
                    color=discord.Color.dark_teal()))

        if 0 > volume or volume > 100:
            raise commands.BadArgument("the volume must be between 0 and 100")
        ctx.voice_state.volume = volume / 100
        await ctx.send(
            embed=discord.Embed(
                title="volume updated",
                description=f'Volume of the player set to {volume}%',
                color=discord.Color.dark_teal()))
    
    @commands.command( aliases=['current', 'playing'])
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def now(self, ctx: GuildVoicedAllowedContext):
        """Displays the currently playing song."""
        if ctx.voice_state.current is None:
            raise NoCurrentMusic()

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(aliases=["next"])
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def skip(self, ctx: GuildVoicedAllowedContext):
        """Skip by vote or requester's decision"""
        voter = ctx.message.author

        if ctx.voice_state.current is None:
            raise NoCurrentMusic()

        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send(f'Skip vote added, currently at **{total_votes}/3**')

        else:
            await ctx.send('You have already voted to skip this song.')
        
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def pause(self, ctx: GuildVoicedAllowedContext):
        """Pauses the currently playing song"""
        if ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def resume(self, ctx: GuildVoicedAllowedContext):
        """Resumes a currently paused song"""
        if ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def stop(self, ctx: GuildVoicedAllowedContext):
        """Stop and clear the music queue"""
        ctx.voice_state.songs.clear()
        if ctx.voice_state.voice_is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command()
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def queue(self, ctx: GuildVoicedAllowedContext, *, page: typing.Optional[int] = 1):
        """List the songs to be played"""
        if len(ctx.voice_state.songs) == 0:
            raise QueueEmpty()
        
        embed = discord.Embed(title ="Queue Musics", description=f'**{len(ctx.voice_state.songs)} tracks:**')

        items_per_page = 9
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        page = page or 1
        start = (page - 1) * items_per_page
        end = start + items_per_page
        embed.set_footer(text=f"Viewing page {page}/{pages}")

        songs = ctx.voice_state.songs[start:end]

        for i, song in enumerate(songs, start=start + 1):
            embed.add_field(name=f'**`{i}.`{song.source.data.title}**',value=f'[Link]({song.source.data.watch_url})\n')

        await ctx.send(embed=embed)

    @commands.command()
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def shuffle(self, ctx: GuildVoicedAllowedContext):
        """Shuffles the queue"""

        if len(ctx.voice_state.songs) == 0:
            raise QueueEmpty()

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command()
    @checks.equals_channel_voice()
    @checks.has_voice_channel_author()
    @checks.has_voice_author()
    @checks.has_voice_client()
    async def remove(self, ctx: GuildVoicedAllowedContext, index: int):
        """Removes a song from the queue at a given index"""

        if len(ctx.voice_state.songs) == 0:
            raise QueueEmpty()

        song = ctx.voice_state.songs[index - 1]
        ctx.voice_state.songs.remove(index - 1)
        await ctx.send(embed=discord.Embed(
            title="music removed",
            description=f"{song.source} removed"  # type: ignore
        ))

    @commands.command(aliases=["song", "music"])
    async def play(self, ctx: GuildVoicedAllowedContext, *, search: str):
        """Plays a new song"""
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if ctx.author.voice.channel != ctx.voice_client.channel:
            raise checks.VoiceError(
                "You are not connected to the Bot's voice channel.")

        async with ctx.typing():
            source = await YouTubeSource.create_source(ctx, search, loop=self.bot.loop)
            song = Song(source)

            await ctx.voice_state.songs.put(song)
            if ctx.voice_state.audio_player.cancelled():
                ctx.voice_state.start_audio_player()
            await ctx.send(embed=discord.Embed(
                title=f'enqueued music',
                description=f"The song '{source}' has been queued",
                color=discord.Color.dark_magenta()))


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
