from __future__ import annotations

import asyncio
import functools
import logging
import os
from typing import TYPE_CHECKING, Callable, TypeVar

import discord

if TYPE_CHECKING:
    from .bot import Bot


CallableT = TypeVar('CallableT', bound=Callable)


MISSING = discord.utils.MISSING


class DiscordWebhookLogger(logging.Handler):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        self.sync_webhook: discord.SyncWebhook = MISSING
        self.async_webhook: discord.Webhook = MISSING
        self.loop: asyncio.AbstractEventLoop | None = None

    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self.send(text)
        else:
            loop.create_task(self.asend(text))

    def send(self, text: str, code: str = 'py') -> None:
        if 'rate limited' in text:
            return

        if self.sync_webhook is MISSING:
            self.sync_webhook = discord.SyncWebhook.from_url(os.environ['LOG_WEBHOOK_URL'])

        embed = discord.Embed(description=f'```{code}\n{text}\n```', color=discord.Color.dark_embed())
        self.sync_webhook.send(embed=embed)

    async def asend(self, text: str, code: str = 'py') -> None:
        if 'rate limited' in text:
            return

        if self.async_webhook is MISSING:
            self.async_webhook = discord.Webhook.from_url(os.environ['LOG_WEBHOOK_URL'], client=self.bot)

        embed = discord.Embed(description=f'```{code}\n{text}\n```', color=discord.Color.dark_embed())
        await self.async_webhook.send(embed=embed)
