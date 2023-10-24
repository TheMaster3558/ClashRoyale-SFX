from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot


class TopGG(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(description='Vote for me!')
    async def vote(self, interaction: discord.Interaction[Bot]) -> None:
        embed = discord.Embed(
            title=f'If you\'re enjoying {interaction.client.user.name}, vote for us on Top.gg!',
            color=0xFF3366,
            url='https://top.gg/bot/924035878895112253/vote',
        )
        embed.set_thumbnail(url='https://blog.top.gg/content/images/size/w2000/2021/12/logo-white-5.png')
        await interaction.followup.send(embed=embed)

    @app_commands.command(description='Review me!')
    async def review(self, interaction: discord.Interaction[Bot]) -> None:
        embed = discord.Embed(
            title=f'If you\'re enjoying {interaction.client.user.name}, please consider leaving a review on Top.gg!',
            url='https://top.gg/bot/924035878895112253#reviews',
            color=0xFF3366,
        )
        embed.set_thumbnail(url='https://blog.top.gg/content/images/size/w2000/2021/12/logo-white-5.png')
        await interaction.followup.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(TopGG(bot))
