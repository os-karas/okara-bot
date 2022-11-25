import typing

from discord.ext import commands
from contexts.all import GuildContext

from contexts.musics import GuildVoicedAllowedContext, GuildVoicedContext


class VoiceError(commands.CheckFailure):
    pass


class BotVoiceNotConnected(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "The Bot not connected to a voice channel.", *args)


class BotVoiceConnected(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "The Bot already connected to a voice channel.", *args)


class AuthorNotConnected(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "You are neither connected to a voice channel.", *args)


class BotNotPermission(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "You are not connected to a voice channel that I have access to.", *args)


class DifferentVoiceChannels(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "You are not connected to the Bot's voice channel.", *args)


class BotNotPlaying(VoiceError):
    def __init__(self, message: typing.Optional[str] = None, *args: typing.Any) -> None:
        super().__init__(message or "The bot is not playing anything.", *args)


def has_voice_client():
    def predicate(ctx: commands.Context):
        if ctx.voice_client is None:
            raise BotVoiceNotConnected()
        return True
    return commands.check(predicate)


def not_has_voice_client():
    def predicate(ctx: commands.Context):
        if ctx.voice_client is not None:
            raise BotVoiceConnected()
        return True
    return commands.check(predicate)


def has_voice_author():
    def predicate(ctx: GuildContext):
        if ctx.author.voice is None:
            raise AuthorNotConnected()
        return True
    return commands.check(predicate)


def has_voice_channel_author():
    def predicate(ctx: GuildVoicedContext):
        if ctx.author.voice.channel is None:
            raise BotNotPermission()
        return True
    return commands.check(predicate)


def equals_channel_voice():
    def predicate(ctx: GuildVoicedAllowedContext):
        if ctx.author.voice.channel != ctx.voice_client.channel:
            raise DifferentVoiceChannels()
        return True
    return commands.check(predicate)
