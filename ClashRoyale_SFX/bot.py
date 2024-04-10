from __future__ import annotations

import datetime
import logging
import os

import aiohttp
import discord
import topgg
from discord import app_commands
from discord.ext import commands, tasks


class Tree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction[Bot]) -> bool:
        if interaction.command:
            await interaction.response.defer()

        return True


class Bot(commands.AutoShardedBot):
    session: aiohttp.ClientSession
    top_gg: topgg.DBLClient

    def __init__(self, test_guild: discord.abc.Snowflake) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, tree_cls=Tree)
        self.test_guild = test_guild
        self.commands_remaining: dict[int, float] = {}

    @tasks.loop(hours=6)
    async def post_guild_count(self) -> None:
        await self.wait_until_ready()
        await self.get_channel(int(os.environ['GUILD_COUNT_CHANNEL_ID'])).send(str(len(self.guilds)))

    @tasks.loop(time=datetime.time(hour=0, minute=0))
    async def reset_commands_remaining(self) -> None:
        self.commands_remaining.clear()

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        logger = logging.getLogger('discord')

        for file in os.listdir(f'{__package__}/cogs'):
            if file.endswith('.py'):
                try:
                    await self.load_extension(f'{__package__}.cogs.{file[:-3]}')
                except Exception as e:
                    logger.error(f'Error loading cog: {file}', exc_info=e)

        await self.load_extension(f'jishaku')

        self.top_gg = topgg.DBLClient(self, os.environ['TOPGG_TOKEN'], autopost=True)

        if 'GUILD_COUNT_CHANNEL_ID' in os.environ:
            self.post_guild_count.start()
        self.reset_commands_remaining.start()

    async def close(self) -> None:
        self.post_guild_count.cancel()
        self.reset_commands_remaining.cancel()
        await self.session.close()
        await self.top_gg.close()
        await super().close()

    @property
    def join_command(self) -> app_commands.Command:
        return self.tree.get_command('join')
