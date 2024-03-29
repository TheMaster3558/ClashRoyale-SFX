import os

import discord
from dotenv import load_dotenv

from .bot import Bot
from .logger import DiscordWebhookLogger

load_dotenv()

test_guild = discord.Object(id=os.environ['TEST_GUILD_ID'])
bot = Bot(test_guild)

if __name__ == '__main__':
    bot.run(os.environ['TOKEN'], log_handler=DiscordWebhookLogger(bot), root_logger=True)
