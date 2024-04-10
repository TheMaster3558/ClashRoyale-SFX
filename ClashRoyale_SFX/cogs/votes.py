from __future__ import annotations

import asyncio
import math
import os
import ssl
import random
from typing import TYPE_CHECKING

import aiohttp_cors
import discord
import topgg
from aiohttp import web
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot


class NoMoreCommands(app_commands.CheckFailure):
    pass


class TopGGVoteButton(discord.ui.Button):
    def __init__(self, bot_url_name: str, bot_id: int) -> None:
        super().__init__(
            label='Vote on Top.gg', url=f'https://top.gg/bot/{bot_id}/vote', emoji='<:topgg_logo:1189808860807049298>'
        )


class TopGGReviewButton(discord.ui.Button):
    def __init__(self, bot_url_name: str, bot_id: int) -> None:
        super().__init__(
            label='Review on Top.gg', url=f'https://top.gg/bot/{bot_id}#reviews', emoji='<:topgg_logo:1189808860807049298>'
        )


class DiscordBotListVoteButton(discord.ui.Button):
    def __init__(self, bot_url_name: str, bot_id: int) -> None:
        super().__init__(
            label='Vote on discordbotlist.com',
            url=f'https://discordbotlist.com/bots/{bot_url_name}/upvote',
            emoji='<:discordbotlist_logo:1189810709236830208>',
        )


class BaseButtonsView(discord.ui.View):
    buttons: tuple[type[discord.ui.Button]]

    def __init__(self, bot: Bot) -> None:
        super().__init__()

        for button_cls in self.buttons:
            self.add_item(button_cls('clashroyale-sfx', bot.application_id))  # type: ignore


class VoteView(BaseButtonsView):
    buttons = (TopGGVoteButton, DiscordBotListVoteButton)


class ReviewView(BaseButtonsView):
    buttons = (TopGGReviewButton,)


class AllView(BaseButtonsView):
    buttons = (TopGGVoteButton, TopGGReviewButton, DiscordBotListVoteButton)


class TopGG(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.webhook_auth = os.environ['WEBHOOK_AUTH']
        self.port = int(os.environ['PORT'])

        self.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook('/topgg', self.webhook_auth)
        cors = aiohttp_cors.setup(self.topgg_webhook.webserver, defaults={
            '*': aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*'
            )
        })
        cors.add(self.topgg_webhook.webserver.router.add_post('/discordbotlist', self.discordbotlist_webhook))

    async def run(self) -> None:
        for webhook in self.topgg_webhook._webhooks.values():
            self.topgg_webhook.webserver.router.add_post(webhook['route'], webhook['func'])
        runner = web.AppRunner(self.topgg_webhook.webserver)
        await runner.setup()

        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.topgg_webhook._webserver = web.TCPSite(
            runner,
            host='0.0.0.0',
            port=self.port,
            ssl_context=ssl_context
        )
        await self.topgg_webhook._webserver.start()

    async def cog_load(self) -> None:
        asyncio.create_task(self.run())

    async def cog_unload(self) -> None:
        await self.topgg_webhook.close()

    async def discordbotlist_webhook(self, request: web.Request) -> web.Response:
        if request.headers.get('Authorization', '') != self.webhook_auth:
            return web.Response(status=401, text='Unauthorized')

        data = await request.json()

        self.bot.dispatch('vote', int(data['id']))
        return web.Response(status=200, text='Ok')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data: topgg.types.BotVoteData) -> None:
        self.bot.dispatch('vote', int(data.user))

    @commands.Cog.listener('on_vote')
    async def on_vote(self, user_id: int) -> None:
        self.bot.commands_remaining[user_id] = math.inf

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction[Bot],
                                        command: app_commands.Command) -> None:
        if random.randint(0, 10) == 0:
            await interaction.followup.send(f'{interaction.user.mention} support me!!🥺🥺',
                                            view=AllView(interaction.client))

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
