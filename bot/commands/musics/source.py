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
                 data: YouTube, volume: float = 0.5):

        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

    def __str__(self):
        return f'**{self.data.title}** by **{self.data.author}**'

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *,
                            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                            volume: float = 0.5):

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

        return cls(ctx,
                   discord.FFmpegPCMAudio(
                       streaming_data["formats"][0]["url"],
                       **cls.FFMPEG_OPTIONS),
                   data=data, volume=volume)

    @ staticmethod
    def parse_duration(durationTime: int):
        minutes, seconds = divmod(durationTime, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration: typing.List[str] = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ", ".join(duration)
