from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING

import topgg
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from aiohttp import web
import aiohttp_cors


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
        self.webhook_port = int(os.environ['WEBHOOK_PORT'])
        self.domain = os.environ['DOMAIN']

        self.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook('/topgg', self.webhook_auth)
        cors = aiohttp_cors.setup(self.topgg_webhook.webserver, defaults={
            '*': aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*'
            )
        })
        cors.add(self.topgg_webhook.webserver.router.add_post('/discordbotlist', self.discordbotlist_webhook))

    async def cog_load(self) -> None:
        await asyncio.create_subprocess_shell(
            f'ngrok http --domain={self.domain} {self.webhook_port}', stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE
        )
        self.topgg_webhook.run(self.webhook_port)

    async def cog_unload(self) -> None:
        await self.topgg_webhook.close()

    async def discordbotlist_webhook(self, request: web.Request) -> web.Response:
        if request.headers.get('Authorization', '') != self.webhook_auth:
            return web.Response(status=401, text='Unauthorized')

        data = await request.json()

        self.bot.dispatch('vote', data['id'])
        return web.Response(status=200, text='Ok')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data: topgg.types.BotVoteData) -> None:
        self.bot.dispatch('vote', data.user)

    @commands.Cog.listener('on_vote')
    async def on_vote(self, user_id: int) -> None:
        self.bot.commands_remaining[user_id] = math.inf

    async def cog_app_command_error(
        self, interaction: discord.Interaction[Bot], error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, NoMoreCommands):
            embed = discord.Embed(
                title='Uh oh, you ran out of commands :(',
                description=f'You *could* either wait {discord.utils.format_dt(self.bot.reset_commands_remaining.next_iteration, style='R')} '
                            f'**OR** you can vote for me to get **UNLIMITED** commands for the **rest of the day**!',
                color=discord.Color.dark_embed()
            ).set_footer(text='Voting only takes 30 seconds so you know what to do😉')
            view = VoteView(interaction.client)
            await interaction.followup.send(embed=embed, view=view)
        else:
            raise error

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
