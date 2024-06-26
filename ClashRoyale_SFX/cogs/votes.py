from __future__ import annotations

import math
import os
import random
from typing import TYPE_CHECKING

import discord
import topgg
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot


class NoMoreCommands(app_commands.CheckFailure):
    pass


class TopGGVoteButton(discord.ui.Button):
    def __init__(self, bot_id: int) -> None:
        super().__init__(
            label='Vote on Top.gg', url=f'https://top.gg/bot/{bot_id}/vote', emoji='<:topgg_logo:1189808860807049298>'
        )


class TopGGReviewButton(discord.ui.Button):
    def __init__(self, bot_id: int) -> None:
        super().__init__(
            label='Review on Top.gg', url=f'https://top.gg/bot/{bot_id}#reviews', emoji='<:topgg_logo:1189808860807049298>'
        )


class BaseButtonsView(discord.ui.View):
    buttons: tuple[type[discord.ui.Button]]

    def __init__(self, bot: Bot) -> None:
        super().__init__()

        for button_cls in self.buttons:
            self.add_item(button_cls(bot.application_id))  # type: ignore


class VoteView(BaseButtonsView):
    buttons = (TopGGVoteButton,)


class ReviewView(BaseButtonsView):
    buttons = (TopGGReviewButton,)


class AllView(BaseButtonsView):
    buttons = (TopGGVoteButton, TopGGReviewButton)


class TopGG(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.webhook_auth = os.environ['WEBHOOK_AUTH']
        self.port = int(os.environ['PORT'])

        self.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook('/topgg', self.webhook_auth)

    async def cog_load(self) -> None:
        self.topgg_webhook.run(self.port)

    async def cog_unload(self) -> None:
        await self.topgg_webhook.close()

    @commands.Cog.listener()
    async def on_dbl_vote(self, data: topgg.types.BotVoteData) -> None:
        self.bot.dispatch('vote', int(data.user))

    @commands.Cog.listener('on_vote')
    async def on_vote(self, user_id: int) -> None:
        self.bot.commands_remaining[user_id] = math.inf

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction[Bot], command: app_commands.Command) -> None:
        if random.randint(0, 10) == 0:
            await interaction.followup.send(f'{interaction.user.mention} support me!!🥺🥺', view=AllView(interaction.client))

    @app_commands.command(description='Vote for me!')
    async def vote(self, interaction: discord.Interaction[Bot]) -> None:
        embed = discord.Embed(
            title=f'If you\'re enjoying me, vote for me🥰!!',
            color=discord.Color.dark_embed(),
        )
        await interaction.followup.send(embed=embed, view=VoteView(self.bot))

    @app_commands.command(description='Review me!')
    async def review(self, interaction: discord.Interaction[Bot]) -> None:
        embed = discord.Embed(
            title=f'If you think im cool, give me a review! 💘💘💘',
            color=discord.Color.dark_embed(),
        )
        await interaction.followup.send(embed=embed, view=ReviewView(self.bot))


async def setup(bot: Bot) -> None:
    await bot.add_cog(TopGG(bot))
