import discord

from discord.ext import commands


class GuildVoiced(discord.Guild):
    voice_client: discord.VoiceClient


class GuildBotVoicedContext(commands.Context):
    guild: GuildVoiced
    author: discord.Member
    voice_client: discord.VoiceClient


class VoicedState(discord.member.VoiceState):
    channel: 'discord.member.VocalGuildChannel'


class AuthorVoicedState(discord.Member):
    voice: 'discord.member.VoiceState'


class AuthorVoicedChannelState(discord.Member):
    voice: VoicedState


class GuildVoicedContext(commands.Context):
    guild: GuildVoiced
    author: AuthorVoicedState
    voice_client: discord.VoiceClient


class GuildVoicedAllowedContext(commands.Context):
    guild: GuildVoiced
    author: AuthorVoicedChannelState
    voice_client: discord.VoiceClient
