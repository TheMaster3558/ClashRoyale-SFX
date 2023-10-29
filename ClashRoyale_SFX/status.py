from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord.ext import tasks

if TYPE_CHECKING:
    from .bot import Bot


@tasks.loop(hours=1)
async def thank_guild(bot: Bot) -> None:
    await bot.wait_until_ready()
    guild = random.choice(bot.guilds)
    await bot.change_presence(activity=discord.CustomActivity(f'Shoutout to {guild}!'))


async def setup(bot: Bot) -> None:
    thank_guild.start(bot)


async def teardown(bot: Bot) -> None:
    thank_guild.cancel()
