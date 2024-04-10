from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .bot import Bot


MISSING = discord.utils.MISSING


class DiscordWebhookLogger(logging.Handler):
    # filled in later by the Bot class

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        self.webhook: discord.Webhook = MISSING

    def emit(self, record: logging.LogRecord) -> None:
        import threading
        print(threading.get_ident(), threading.main_thread().ident)
        text = self.format(record)
        asyncio.create_task(self.send(text))

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
