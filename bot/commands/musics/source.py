import discord
import asyncio


from discord.ext import commands
from pytube import exceptions as pytube_erros
from pytube import YouTube


class SourceError(commands.CommandError):
    pass


class YouTubeSource():
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, ctx: commands.Context, source: str, *,
                 data: YouTube, volume: float = 1.0):

        self.volume = volume
        self._source_link = source

        self.ctx = ctx

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

    def audio_source(self):
        return discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                self._source_link,
                **self.FFMPEG_OPTIONS),
            self.volume)

    def __str__(self):
        return f'**{self.data.title}** by **{self.data.author}**'

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
                   streaming_data["formats"]
                   [int(formats_quantity / 2)]
                   ["url"],
                   data=data, volume=volume)
