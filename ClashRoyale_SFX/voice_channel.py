from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot


class Basic(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

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
            await interaction.user.voice.channel.connect()
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
