from __future__ import annotations

import asyncio
import os
import random

import aiohttp
import discord
import topgg
from discord import app_commands
from discord.ext import commands


class Tree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction[Bot]) -> bool:
        await interaction.response.defer()

        if random.randint(1, 5) == 1:
            cmds = (self.get_command('vote'), self.get_command('review'))
            cmd = random.choice(cmds)

            async def wait_then_execute() -> None:
                await asyncio.sleep(5)
                await cmd.callback(interaction.client.get_cog('top_gg'), interaction)

            asyncio.create_task(wait_then_execute())

        return True


class Bot(commands.AutoShardedBot):
    session: aiohttp.ClientSession
    top_gg: topgg.DBLClient

    def __init__(self, test_guild: discord.abc.Snowflake) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, tree_cls=Tree)
        self.test_guild = test_guild

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        module = os.path.dirname(os.path.realpath(__file__)).split('\\')[-1].split('/')[-1]

        await self.load_extension(f'{module}.voice_channel')
        await self.load_extension(f'{module}.clash_royale_audio')
        await self.load_extension(f'{module}.top_gg')
        await self.load_extension(f'jishaku')

        # await self.tree.sync()
        self.top_gg = topgg.DBLClient(self, os.environ['TOPGG_TOKEN'], autopost=True)

    async def close(self) -> None:
        await self.session.close()
        await self.top_gg.close()
        await super().close()

    @property
    def join_command(self) -> app_commands.Command:
        return self.tree.get_command('join')
