from os import environ
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all())


bot = Bot()

bot.run("")
