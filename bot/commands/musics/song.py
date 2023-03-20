import asyncio
import discord
import itertools
import random

from .source import YouTubeSource
from discord.ext import commands
from typing import List

class QueueEmpty(commands.CommandError):
    def __init__(self) -> None:
        super().__init__("Song Queue is empty")

class NoCurrentMusic(commands.CommandError):
    def __init__(self) -> None:
        super().__init__("Nothing being played at the moment")


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YouTubeSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description=f'```css\n{self.source.data.title}\n```',
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.parse_duration(self.source.data.length))
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value=f'[{self.source.data.author}]({self.source.data.channel_url})')
                 .add_field(name='URL', value=f'[Click]({self.source.data.watch_url})')
                 .set_thumbnail(url=self.source.data.thumbnail_url)
                 )

        return embed

    @staticmethod
    def parse_duration(durationTime: int):
        minutes, seconds = divmod(durationTime, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f"{days} day{'s' if days > 1 else '' }")
        if hours > 0:
            duration.append(f"{hours} hour{'s' if hours > 1 else '' }")
        if minutes > 0:
            duration.append(f"{minutes} minute{'s' if minutes > 1 else '' }")
        if seconds > 0:
            duration.append(f"{seconds} second{'s' if seconds > 1 else '' }")

        if len(duration) >= 2:
            duration = [", ".join(duration[:-1]), duration[-1]]
            return " and ".join(duration)

        return duration[0]


class SongQueue(asyncio.Queue):

    def __init__(self, maxsize: int = 0) -> None:
        self._queue: List[Song] = []
        super().__init__(maxsize)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]
