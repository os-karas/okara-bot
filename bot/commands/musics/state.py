import asyncio
import logging
import discord

from bot.contexts.all import GuildContext
from discord.ext import commands
from .song import Song, SongQueue
from async_timeout import timeout


class VoiceError(Exception):
    pass


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self._next = asyncio.Event()
        self._voice: discord.VoiceClient | None = ctx.voice_client # type: ignore
        self.current: Song | None = None
        self.songs: SongQueue = SongQueue()

        self.loop: bool = False
        self._volume: float = 1.0
        self.skip_votes: set = set()

        self.start_audio_player()

    def __del__(self):
        self._audio_player.cancel()

    @property
    def voice(self) -> discord.VoiceClient: 
        return self._ctx.voice_client # type: ignore

    @property
    def volume(self):
        return self._volume

    @property
    def audio_player(self):
        return self._audio_player

    @volume.setter
    def volume(self, value: float):
        self._volume = value
        if (self.current and self.current.source):
            self.current.source.set_volume(self.volume)

    @property
    def voice_is_playing(self):
        if self.voice:
            return self.voice.is_playing() or self.voice.is_paused()
        else:
            return False
    
    def start_audio_player(self):
        self._audio_player = self.bot.loop.create_task(self._audio_player_task())
    

    async def _audio_player_task(self):
        while True:
            self._next.clear()

            # Try to get the next song within 3 minutes.
            # If no song will be added to the queue in time,
            # the player will disconnect due to performance
            # reasons.
            try:
                async with timeout(180):  # 3 minutes
                    self.current: Song | None = await self.songs.get()
            except asyncio.TimeoutError:
                self.bot.loop.create_task(self.stop())
                self._audio_player.cancel()
                break

            if self.current is None or self.voice is None:
                continue

            self.voice.play(self.current.source.get_audio_source(),
                            after=self._play_next_song)

            await self.current.source.channel.send(embed=self.current.create_embed())
            last_current = self.current
            # em caso de loop a ultima musica será adicionada ao final
            await self._next.wait()
            if self.loop:
                await self.songs.put(last_current)
        

    def _play_next_song(self, error=None):
        if error:
            logging.warning(error)
        self.next()

    def clear(self):
        self.current = None
        self.songs.clear()
    
    def next(self):
        self.current = None
        self._next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.voice_is_playing:
            self.voice.stop()

    async def stop(self):
        self.clear()

        if self.voice:
            await self.voice.disconnect()
        
    
class VoiceStateContext(GuildContext):
    voice_state: VoiceState