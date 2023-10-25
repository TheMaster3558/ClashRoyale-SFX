from __future__ import annotations

from typing import TYPE_CHECKING

import asyncio
import logging
import os

import discord

if TYPE_CHECKING:
    from .bot import Bot


MISSING = discord.utils.MISSING


class DiscordWebhookLogger(logging.Handler):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        self.webhook: discord.Webhook = MISSING

        self.asyncio_lock = asyncio.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)
        asyncio.create_task(self.send(text))

    async def send(self, text: str) -> None:
        async with self.asyncio_lock:
            while not hasattr(self.bot, 'session'):
                await asyncio.sleep(0)

            if not self.webhook:
                self.webhook = discord.Webhook.from_url(os.environ['LOG_WEBHOOK_URL'], session=self.bot.session, client=self.bot)
            await self.webhook.send(text)

