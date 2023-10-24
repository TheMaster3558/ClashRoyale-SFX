import os

import discord
from dotenv import load_dotenv

from .bot import Bot

load_dotenv()

test_guild = discord.Object(id=os.getenv('TEST_GUILD_ID'))
bot = Bot(test_guild)

if __name__ == '__main__':
    #os.environ['PATH'] += os.pathsep + os.path.join(os.getcwd(), 'ffmpeg')
    bot.run(os.getenv('TOKEN'))
