from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot


class Basic(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        if not before.channel:
            return

        voice_client = (
            before.channel.guild.voice_client
        )  # don't use member because this function may trigger if they leave the guild

        if (
            voice_client is not None
            and after.channel is None
            and before.channel == voice_client.channel
            and len(before.channel.members) == 1
        ):
            await voice_client.disconnect(force=False)

    @app_commands.command(description='Join your current voice channel!')
    async def join(self, interaction: discord.Interaction[Bot]) -> bool:
        if not interaction.user.voice:
            await interaction.followup.send('You must join a voice channel first.')
            return False
        elif interaction.guild.voice_client:
            if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                await interaction.followup.send('I am busy.')
                return False
            return True
        else:
            try:
                await interaction.user.voice.channel.connect()
            except asyncio.TimeoutError:
                await interaction.followup.send('Connecting to your voice channel failed.')
                return False
            else:
                await interaction.followup.send('Joined!')
                return True

    @app_commands.command(description='Leave your current voice channel.')
    async def leave(self, interaction: discord.Interaction[Bot]) -> None:
        if not interaction.guild.voice_client:
            await interaction.followup.send('I am not in a voice channel rn.')
        elif not interaction.user.voice or interaction.user.voice.channel != interaction.guild.voice_client.channel:
            await interaction.followup.send('You must be in my channel.')
        else:
            await interaction.guild.voice_client.disconnect(force=False)
            await interaction.followup.send('Left.')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Basic(bot))
