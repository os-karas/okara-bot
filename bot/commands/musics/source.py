import discord
import asyncio
import typing


from discord.ext import commands
from pytube import exceptions as pytube_erros
from pytube import YouTube


class SourceError(commands.CommandError):
    pass


class YouTubeSource(discord.PCMVolumeTransformer):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *,
                 data: YouTube, volume: float = 1.0):

        super().__init__(source, volume)

        self.ctx = ctx

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

    def __str__(self):
        return f'**{self.data.title}** by **{self.data.author}**'

    
    def clone(self):
        return self.create_source(self.ctx, self.data.watch_url, loop = asyncio.get_event_loop(), volume = self.volume)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *,
                            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                            volume: float = 1):

        # raise commands.CheckFailure("Error in bot")
        try:
            data = await loop.run_in_executor(
                None, lambda search: YouTube(search), search)
        except pytube_erros.VideoPrivate as err:
            raise SourceError(
                f"The song `{err.video_id}` is private")
        except pytube_erros.MembersOnly as err:
            raise SourceError(
                f"The song `{err.video_id}` is for member only")
        except pytube_erros.VideoRegionBlocked as err:
            raise SourceError(
                f"The song `{err.video_id}` blocked in my region")
        except pytube_erros.VideoUnavailable as err:
            raise SourceError(f"`The song `{search}` not found")
        except pytube_erros.RegexMatchError:
            raise SourceError(f"`{search}` nor a valid link")
        except pytube_erros.PytubeError:
            raise SourceError("Error searching music")

        try:
            streaming_data = data.streaming_data
            if not "formats" in streaming_data:
                raise SourceError(f"Live is not supported")
        except:
            raise SourceError(f"Could not get the music `{search}`")

        formats_quantity = len(streaming_data["formats"])
        return cls(ctx,
                   discord.FFmpegPCMAudio(
                       streaming_data["formats"]
                       [int(formats_quantity / 2)]
                       ["url"],
                       **cls.FFMPEG_OPTIONS),
                   data=data, volume=volume)

