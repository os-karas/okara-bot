import discord

from bot.commands.musics.state import VoiceStateContext


class GuildVoiced(discord.Guild):
    voice_client: discord.VoiceClient


class GuildBotVoicedContext(VoiceStateContext):
    guild: GuildVoiced
    author: discord.Member
    voice_client: discord.VoiceClient


class VoicedState(discord.member.VoiceState):
    channel: 'discord.member.VocalGuildChannel'


class AuthorVoicedState(discord.Member):
    voice: 'discord.member.VoiceState'


class AuthorVoicedChannelState(discord.Member):
    voice: VoicedState


class GuildVoicedContext(VoiceStateContext):
    guild: GuildVoiced
    author: AuthorVoicedState
    voice_client: discord.VoiceClient


class GuildVoicedAllowedContext(VoiceStateContext):
    guild: GuildVoiced
    author: AuthorVoicedChannelState
    voice_client: discord.VoiceClient
