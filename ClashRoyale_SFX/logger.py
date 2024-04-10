from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .bot import Bot


MISSING = discord.utils.MISSING


class DiscordWebhookLogger(logging.Handler):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        self.webhook: discord.Webhook = MISSING
        self.loop: asyncio.AbstractEventLoop | None = None

    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)

        try:
            asyncio.create_task(self.send(text))
        except RuntimeError:
            # no event loop is present as this is being called from another thread for some reason
            while self.loop is None:
                time.sleep(1)
            asyncio.run_coroutine_threadsafe(self.send(text), self.loop)

    async def send(self, text: str, code: str = 'py') -> None:
        while not hasattr(self.bot, 'session'):
            await asyncio.sleep(0)

        if not self.webhook:
            self.webhook = discord.Webhook.from_url(os.environ['LOG_WEBHOOK_URL'], session=self.bot.session, client=self.bot)

        embed = discord.Embed(description=f'```{code}\n{text}\n```', color=discord.Color.dark_embed())

        try:
            await self.webhook.send(embed=embed)
        except discord.HTTPException:
            # without this catch, a ratelimit could send the bot into an infinite loop
            # error -> log the error -> rate limit -> error -> ...
            pass
