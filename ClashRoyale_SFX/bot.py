from __future__ import annotations

import asyncio
import logging
import os
import random
from pathlib import Path

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

    @tasks.loop(hours=6)
    async def post_guild_count(self) -> None:
        await self.wait_until_ready()
        await self.get_channel(int(os.environ['GUILD_COUNT_CHANNEL_ID'])).send(str(len(self.guilds)))

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        logger = logging.getLogger('discord')
        for file in Path('cogs').glob('**/*.py'):
            *tree, _ = file.parts
            try:
                await self.load_extension(f"{'.'.join(tree)}.{file.stem}")
            except Exception as e:
                logger.error(f'Error loading cog: {file.stem}', exc_info=e)

        await self.load_extension(f'jishaku')

        # await self.tree.sync()
        self.top_gg = topgg.DBLClient(self, os.environ['TOPGG_TOKEN'], autopost=True)

        if 'GUILD_COUNT_CHANNEL_ID' in os.environ:
            self.post_guild_count.start()

    async def close(self) -> None:
        self.post_guild_count.cancel()
        await self.session.close()
        await self.top_gg.close()
        await super().close()

    @property
    def join_command(self) -> app_commands.Command:
        return self.tree.get_command('join')
